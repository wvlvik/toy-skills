#!/usr/bin/env python3
"""
Alibaba Cloud OSS Upload Script
Supports: single file, directory, and large file resumable upload
SDK: alibabacloud-oss-v2 (Python SDK v2)
Docs: https://www.alibabacloud.com/help/en/oss/developer-reference/overview-of-oss-sdk-for-python-v2
"""

import os
import sys
import argparse
import json
import mimetypes
import re
import hashlib
import time
import select
from pathlib import Path
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

try:
    import alibabacloud_oss_v2 as oss
    from alibabacloud_oss_v2 import exceptions
except ImportError:
    print("Installing alibabacloud-oss-v2...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--break-system-packages", "alibabacloud-oss-v2"])
    import alibabacloud_oss_v2 as oss
    from alibabacloud_oss_v2 import exceptions


class OSSUploader:
    """Client for uploading files to Alibaba Cloud OSS"""

    def __init__(
        self,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
        region: Optional[str] = None,
        bucket: Optional[str] = None,
    ):
        self.access_key_id = access_key_id or os.environ.get("OSS_ACCESS_KEY_ID")
        self.access_key_secret = access_key_secret or os.environ.get(
            "OSS_ACCESS_KEY_SECRET"
        )
        self.region = region or os.environ.get("OSS_REGION", "cn-hangzhou")
        self.bucket = bucket or os.environ.get("OSS_BUCKET")

        if not self.access_key_id or not self.access_key_secret:
            raise ValueError(
                "OSS credentials required. Set OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET "
                "environment variables, or pass them as arguments."
            )

        self._client: Optional[oss.Client] = None

    @property
    def client(self) -> oss.Client:
        if self._client is None:
            credentials_provider = oss.credentials.StaticCredentialsProvider(
                self.access_key_id, self.access_key_secret
            )
            cfg = oss.config.load_default()
            cfg.credentials_provider = credentials_provider
            cfg.region = self.region
            self._client = oss.Client(cfg)
        return self._client

    def _get_content_type(self, file_path: str) -> str:
        """Guess content type from file extension"""
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or "application/octet-stream"

    def _make_progress_callback(self, desc: str = "Uploading") -> Callable:
        """Create a progress callback function"""
        state = {"last_percent": -1}

        def callback(n: int, written: int, total: int) -> None:
            if total > 0:
                percent = int(100 * written / total)
                if percent != state["last_percent"]:
                    state["last_percent"] = percent
                    bar_len = 30
                    filled = int(bar_len * percent / 100)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    print(f"\r{desc}: [{bar}] {percent}%", end="", flush=True)
                    if percent == 100:
                        print()

        return callback

    def _get_oss_url(self, bucket: str, key: str) -> str:
        """Generate the public OSS URL for an object"""
        return f"https://{bucket}.oss-{self.region}.aliyuncs.com/{key}"

    def upload_file(
        self,
        local_path: str,
        key: Optional[str] = None,
        bucket: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        storage_class: Optional[str] = None,
        acl: Optional[str] = None,
        quiet: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload a single file to OSS.

        Args:
            local_path: Path to the local file
            key: OSS object key (defaults to filename)
            bucket: Target bucket (uses default if not specified)
            content_type: MIME type (auto-detected if not specified)
            metadata: Custom metadata headers
            storage_class: Storage class (Standard, IA, Archive)
            acl: Access control (private, public-read, public-read-write)
            quiet: Suppress progress output

        Returns:
            Dict with upload result including URL and details
        """
        path = Path(local_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {local_path}")

        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError(
                "Bucket name required. Set OSS_BUCKET env var or pass --bucket"
            )

        key = key or path.name
        content_type = content_type or self._get_content_type(str(path))

        progress_fn = (
            None if quiet else self._make_progress_callback(f"Uploading {path.name}")
        )

        try:
            request = oss.PutObjectRequest(
                bucket=bucket,
                key=key,
                content_type=content_type,
            )

            if metadata:
                request.metadata = metadata
            if storage_class:
                request.storage_class = storage_class
            if acl:
                request.acl = acl
            if progress_fn:
                request.progress_fn = progress_fn

            result = self.client.put_object_from_file(request, str(path))

            url = self._get_oss_url(bucket, key)

            return {
                "success": True,
                "url": url,
                "bucket": bucket,
                "key": key,
                "etag": result.etag,
                "crc64": result.hash_crc64,
                "request_id": result.request_id,
                "size": path.stat().st_size,
            }

        except exceptions.ServiceError as e:
            return {
                "success": False,
                "error": {
                    "code": e.error_code,
                    "message": e.message,
                    "status_code": e.status_code,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "upload_failed",
                    "message": str(e),
                },
            }

    def upload_large_file(
        self,
        local_path: str,
        key: Optional[str] = None,
        bucket: Optional[str] = None,
        part_size: int = 6 * 1024 * 1024,  # 6 MB default
        parallel_num: int = 3,
        enable_checkpoint: bool = True,
        checkpoint_dir: Optional[str] = None,
        quiet: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload a large file with multipart and optional resumable upload.

        Args:
            local_path: Path to the local file
            key: OSS object key
            bucket: Target bucket
            part_size: Size of each part in bytes (default: 6 MB)
            parallel_num: Number of parallel uploads
            enable_checkpoint: Enable resumable upload
            checkpoint_dir: Directory for checkpoint files
            quiet: Suppress progress output

        Returns:
            Dict with upload result
        """
        path = Path(local_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {local_path}")

        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required")

        key = key or path.name

        progress_fn = (
            None if quiet else self._make_progress_callback(f"Uploading {path.name}")
        )

        try:
            uploader_kwargs: Dict[str, Any] = {
                "part_size": part_size,
                "parallel_num": parallel_num,
            }

            if enable_checkpoint:
                uploader_kwargs["enable_checkpoint"] = True
                uploader_kwargs["checkpoint_dir"] = checkpoint_dir or os.environ.get(
                    "OSS_CHECKPOINT_DIR", "/tmp/oss_checkpoints"
                )

            uploader = self.client.uploader(**uploader_kwargs)

            request = oss.PutObjectRequest(bucket=bucket, key=key)
            if progress_fn:
                request.progress_fn = progress_fn

            result = uploader.upload_file(request, filepath=str(path))

            url = self._get_oss_url(bucket, key)

            return {
                "success": True,
                "url": url,
                "bucket": bucket,
                "key": key,
                "etag": result.etag,
                "request_id": result.request_id,
                "size": path.stat().st_size,
                "multipart": True,
            }

        except exceptions.ServiceError as e:
            return {
                "success": False,
                "error": {
                    "code": e.error_code,
                    "message": e.message,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "upload_failed",
                    "message": str(e),
                },
            }

    def upload_directory(
        self,
        local_dir: str,
        oss_prefix: str,
        bucket: Optional[str] = None,
        pattern: str = "*",
        recursive: bool = True,
        sanitize_filenames: bool = False,
        quiet: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload all files in a directory to OSS.

        Args:
            local_dir: Path to the local directory
            oss_prefix: OSS key prefix (folder path in bucket)
            bucket: Target bucket
            pattern: File pattern to match (e.g., "*.jpg")
            recursive: Include subdirectories
            sanitize_filenames: Sanitize filenames with Chinese/special chars to safe MD5 names
            quiet: Suppress progress output

        Returns:
            Dict with upload summary and individual file results
        """
        dir_path = Path(local_dir)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {local_dir}")

        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required")

        results: List[Dict[str, Any]] = []
        success_count = 0
        fail_count = 0
        total_size = 0

        # Collect files
        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))

        # Filter out hidden files and files in hidden directories
        files = [
            f for f in files 
            if f.is_file() and not any(part.startswith('.') for part in f.relative_to(dir_path).parts)
        ]

        if not files:
            return {
                "success": True,
                "message": "No files found matching pattern",
                "files": [],
            }

        if not quiet:
            print(f"Found {len(files)} file(s) to upload")

        for file_path in files:
            rel_path = file_path.relative_to(dir_path)
            original_name = file_path.name
            
            # Sanitize filename if requested
            if sanitize_filenames:
                safe_name = self._sanitize_filename(original_name)
                # Rebuild relative path with sanitized filename
                rel_path_parts = list(rel_path.parts)
                if rel_path_parts:
                    rel_path_parts[-1] = safe_name
                    sanitized_rel_path = "/".join(rel_path_parts)
                else:
                    sanitized_rel_path = safe_name
                oss_key = f"{oss_prefix}/{sanitized_rel_path}"
            else:
                safe_name = original_name
                oss_key = f"{oss_prefix}/{rel_path}".replace("\\", "/")

            if not quiet:
                status = f"[{success_count + fail_count + 1}/{len(files)}]"
                if sanitize_filenames and safe_name != original_name:
                    print(f"{status} {original_name} -> {safe_name}")
                else:
                    print(f"\n{status} {original_name}")

            result = self.upload_file(
                str(file_path),
                key=oss_key,
                bucket=bucket,
                quiet=quiet,
            )

            # Add filename info for directory upload
            result["original_name"] = original_name
            if sanitize_filenames:
                result["safe_name"] = safe_name
                result["was_renamed"] = safe_name != original_name

            results.append(result)

            if result.get("success"):
                success_count += 1
                total_size += result.get("size", 0)
            else:
                fail_count += 1

        return {
            "success": fail_count == 0,
            "bucket": bucket,
            "prefix": oss_prefix,
            "total_files": len(files),
            "success_count": success_count,
            "fail_count": fail_count,
            "total_size": total_size,
            "sanitize_filenames": sanitize_filenames,
            "files": results,
        }
    def upload_image(
        self,
        local_path: str,
        key: Optional[str] = None,
        bucket: Optional[str] = None,
        acl: str = "public-read",
        quiet: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload an image file with public-read ACL.

        Args:
            local_path: Path to the image file
            key: OSS object key
            bucket: Target bucket
            acl: Access control (default: public-read)
            quiet: Suppress progress output

        Returns:
            Dict with upload result and image URL
        """
        path = Path(local_path)
        content_type = self._get_content_type(str(path))

        # Validate image type
        image_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
        ]
        if content_type not in image_types:
            print(f"Warning: {content_type} may not be an image type", file=sys.stderr)

        return self.upload_file(
            local_path,
            key=key,
            bucket=bucket,
            content_type=content_type,
            acl=acl,
            quiet=quiet,
        )

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename: if contains Chinese or special characters, generate a safe name.
        Returns sanitized filename.
        """
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        
        # Pattern for safe filename: alphanumeric, underscore, hyphen, dot
        if re.match(r'^[a-zA-Z0-9_.-]+$', stem):
            return filename
        
        # Generate safe name using hash of original + timestamp
        hash_input = f"{stem}{time.time()}"
        safe_stem = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        return f"{safe_stem}{suffix}"

    def upload_images(
        self,
        image_paths: List[str],
        key_prefix: str = "statics/i/img",
        bucket: Optional[str] = None,
        acl: str = "public-read",
        quiet: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload multiple image files with automatic filename sanitization.

        Args:
            image_paths: List of local image file paths
            key_prefix: OSS key prefix (default: statics/i/img)
            bucket: Target bucket
            acl: Access control (default: public-read)
            quiet: Suppress progress output

        Returns:
            Dict with upload results including sanitized keys
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name required")

        results: List[Dict[str, Any]] = []
        success_count = 0
        fail_count = 0

        if not quiet:
            print(f"Uploading {len(image_paths)} image(s)...")

        for idx, image_path in enumerate(image_paths, 1):
            path = Path(image_path)
            if not path.exists():
                results.append({
                    "success": False,
                    "original_path": image_path,
                    "error": "File not found",
                })
                fail_count += 1
                continue

            # Sanitize filename if needed
            original_name = path.name
            safe_name = self._sanitize_filename(original_name)
            oss_key = f"{key_prefix}/{safe_name}"

            if not quiet:
                status = f"[{idx}/{len(image_paths)}]"
                if safe_name != original_name:
                    print(f"{status} {original_name} -> {safe_name}")
                else:
                    print(f"{status} {original_name}")

            result = self.upload_image(
                image_path,
                key=oss_key,
                bucket=bucket,
                acl=acl,
                quiet=quiet,
            )

            # Add extra info for multi-image upload
            if result.get("success"):
                result["original_name"] = original_name
                result["safe_name"] = safe_name
                result["was_renamed"] = safe_name != original_name
                success_count += 1
            else:
                result["original_name"] = original_name
                fail_count += 1

            results.append(result)

        return {
            "success": fail_count == 0,
            "bucket": bucket,
            "key_prefix": key_prefix,
            "total_images": len(image_paths),
            "success_count": success_count,
            "fail_count": fail_count,
            "images": results,
        }


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable size"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes = size_bytes / 1024
    return f"{size_bytes:.1f} TB"

def parse_path_input(line: str) -> List[str]:
    """
    Parse a line of input and extract valid file paths.
    Supports:
    - Plain file paths (with spaces)
    - file:// URLs
    - Multiple space-separated paths (when paths don't contain spaces)
    - Quoted paths
    """
    from urllib.parse import unquote, urlparse
    
    paths = []
    line = line.strip()
    
    if not line:
        return paths
    
    # Handle file:// URLs
    if 'file://' in line:
        # Extract file:// URLs
        file_url_pattern = re.compile(r'file://([^\s]+)')
        matches = file_url_pattern.findall(line)
        for match in matches:
            try:
                parsed = urlparse(f'file://{match}')
                path = unquote(parsed.path)
                # On macOS, file URLs start with /, on Windows they might not
                if path and not Path(path).is_absolute() and sys.platform == 'win32':
                    path = path.lstrip('/')
                paths.append(path)
            except Exception:
                pass
        # Remove file:// URLs from line for further processing
        line = file_url_pattern.sub('', line).strip()
    
    if not line:
        return paths
    
    # Check if line looks like a single path (exists or contains path separators)
    test_path = Path(line)
    if test_path.exists() or '/' in line or '\\' in line:
        # Treat entire line as a single path
        paths.append(line)
        return paths
    
    # Try to split by common delimiters but validate each part
    # First, try space-separated paths
    parts = line.split()
    if len(parts) > 1:
        valid_parts = []
        for part in parts:
            # Check if this looks like a path
            if Path(part).exists() or '/' in part or '\\' in part or part.startswith('~'):
                valid_parts.append(part)
        
        # If all parts look like paths, use them
        if valid_parts and len(valid_parts) == len(parts):
            paths.extend(valid_parts)
            return paths
        # If some parts are valid paths, still use them
        elif valid_parts:
            paths.extend(valid_parts)
            return paths
    
    # Fallback: treat the entire line as a single path
    paths.append(line)
    return paths


def validate_and_expand_path(path_str: str) -> Optional[str]:
    """
    Validate and expand a path string.
    Returns the expanded absolute path if valid, None otherwise.
    """
    try:
        # Expand ~ to home directory
        expanded = os.path.expanduser(path_str)
        # Expand environment variables
        expanded = os.path.expandvars(expanded)
        # Normalize the path
        expanded = os.path.normpath(expanded)
        
        path = Path(expanded)
        if path.exists() and path.is_file():
            return str(path.resolve())
        return None
    except Exception:
        return None


def get_paths_from_input() -> List[str]:
    """
    Get file paths from user input.
    Priority: stdin pipe > interactive prompt
    
    Supports:
    - Plain file paths (including paths with spaces)
    - file:// URLs
    - Multiple paths (one per line or space-separated)
    - Tilde expansion (~)
    - Environment variables in paths
    """
    raw_paths = []
    
    # Check if data is available on stdin (piped input)
    if not sys.stdin.isatty():
        try:
            # Set stdin to non-blocking mode for quick check
            if select.select([sys.stdin], [], [], 0.1)[0]:
                for line in sys.stdin:
                    line = line.strip()
                    if line:
                        raw_paths.extend(parse_path_input(line))
        except Exception:
            pass
    
    # If no stdin input, prompt user interactively
    if not raw_paths:
        print("\nEnter file paths to upload (one per line, empty line to finish):")
        print("  Supported formats:")
        print("    - Plain path: /Users/me/photo.jpg")
        print("    - Path with spaces: /Users/me/My Photos/photo.jpg")
        print("    - file:// URL: file:///Users/me/photo.jpg")
        print("    - Home directory: ~/Desktop/photo.png")
        print("  Or paste multiple paths (one per line):")
        print("-" * 50)
        
        try:
            while True:
                try:
                    line = input()
                    if not line.strip():
                        break
                    raw_paths.extend(parse_path_input(line))
                except EOFError:
                    break
        except KeyboardInterrupt:
            print("\n\nInput cancelled.")
            return []
    
    # Validate and expand paths
    valid_paths = []
    invalid_paths = []
    
    # Remove duplicates while preserving order
    seen = set()
    unique_raw = []
    for p in raw_paths:
        if p not in seen:
            seen.add(p)
            unique_raw.append(p)
    
    for raw_path in unique_raw:
        expanded = validate_and_expand_path(raw_path)
        if expanded:
            if expanded not in valid_paths:  # Avoid duplicates after expansion
                valid_paths.append(expanded)
        else:
            invalid_paths.append(raw_path)
    
    # Report invalid paths
    if invalid_paths:
        print("\nWarning: The following paths were not found or are not files:", file=sys.stderr)
        for p in invalid_paths:
            print(f"  - {p}", file=sys.stderr)
    
    return valid_paths

def main():
    parser = argparse.ArgumentParser(
        description="Upload files to Alibaba Cloud OSS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload a single file
  %(prog)s file.txt --bucket my-bucket
  %(prog)s photo.jpg --key images/2024/photo.jpg --bucket my-bucket
  # Upload multiple images (auto-sanitize Chinese/special chars)
  %(prog)s img1.jpg img2.png --images --bucket my-bucket
  %(prog)s photo1.jpg "照片.jpg" --images --bucket my-bucket --prefix statics/i/img
  # Upload directory
  %(prog)s ./images --prefix assets/images --bucket my-bucket
  %(prog)s video.mp4 --bucket my-bucket --large
  # Upload single image with public access
  %(prog)s photo.jpg --bucket my-bucket --image
  OSS_ACCESS_KEY_ID       Access Key ID (required)
  OSS_ACCESS_KEY_SECRET   Access Key Secret (required)
  OSS_REGION              Region (default: cn-hangzhou)
  OSS_BUCKET              Default bucket name
        """,
    )

    parser.add_argument("paths", nargs="*", help="Local file or directory paths to upload")
    parser.add_argument("--bucket", "-b", help="OSS bucket name (or set OSS_BUCKET)")
    parser.add_argument("--key", "-k", help="OSS object key (default: filename)")
    parser.add_argument("--prefix", "-p", help="OSS key prefix (default for images: statics/i/img)")
    parser.add_argument(
        "--region",
        "-r",
        default=None,
        help="OSS region (default: from OSS_REGION env or cn-hangzhou)",
    )
    # Upload modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--large",
        "-l",
        action="store_true",
        help="Use multipart upload for large files",
    )
    mode_group.add_argument(
        "--image", "-i", action="store_true", help="Upload single image with public access"
    )
    mode_group.add_argument(
        "--images", action="store_true", help="Upload multiple images (supports multiple paths)"
    )
    mode_group.add_argument("--dir", "-d", action="store_true", help="Upload directory")
    parser.add_argument(
        "--acl",
        choices=["private", "public-read", "public-read-write"],
        help="Object ACL",
    )
    parser.add_argument(
        "--storage-class", choices=["Standard", "IA", "Archive"], help="Storage class"
    )
    parser.add_argument(
        "--pattern", default="*", help="File pattern for directory upload (default: *)"
    )
    parser.add_argument(
        "--no-recursive", action="store_true", help="Don't include subdirectories"
    )
    parser.add_argument(
        "--sanitize", "-s", action="store_true",
        help="Sanitize filenames with Chinese/special chars to safe MD5 names (for directory upload)"
    )
    parser.add_argument(
        "--part-size",
        type=int,
        default=6,
        help="Part size in MB for large files (default: 6)",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=3,
        help="Parallel uploads for large files (default: 3)",
    )
    parser.add_argument(
        "--no-checkpoint", action="store_true", help="Disable resumable upload"
    )
    # Output
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress output"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Validate paths - if not provided, try to get from user input
    if not args.paths:
        args.paths = get_paths_from_input()
        if not args.paths:
            print("Error: No paths specified", file=sys.stderr)
            parser.print_help()
            sys.exit(1)

    # For --images mode, all paths should be validated
    if args.images:
        for p in args.paths:
            if not Path(p).exists():
                print(f"Error: File not found: {p}", file=sys.stderr)
                sys.exit(1)
    else:
        # Single path mode
        path = Path(args.paths[0])
        if not path.exists():
            print(f"Error: Path not found: {args.paths[0]}", file=sys.stderr)
            sys.exit(1)

    try:
        # Use region from args, env var, or default
        region = args.region or os.environ.get("OSS_REGION", "cn-hangzhou")
        
        # Debug: Check environment variables
        env_check = {
            "OSS_ACCESS_KEY_ID": "✓ set" if os.environ.get("OSS_ACCESS_KEY_ID") else "✗ NOT SET",
            "OSS_ACCESS_KEY_SECRET": "✓ set" if os.environ.get("OSS_ACCESS_KEY_SECRET") else "✗ NOT SET",
            "OSS_REGION": os.environ.get("OSS_REGION", "✗ NOT SET (will use default: cn-hangzhou)"),
            "OSS_BUCKET": os.environ.get("OSS_BUCKET", "✗ NOT SET (must use --bucket)"),
        }
        
        if not args.quiet:
            print("\nEnvironment variables check:")
            for key, status in env_check.items():
                print(f"  {key}: {status}")
            print()
        
        uploader = OSSUploader(region=region, bucket=args.bucket)
        if args.images:
            # Multi-image upload mode
            key_prefix = args.prefix or "statics/i/img"
            result = uploader.upload_images(
                args.paths,
                key_prefix=key_prefix,
                acl=args.acl or "public-read",
                quiet=args.quiet,
            )

        elif args.dir or (len(args.paths) == 1 and Path(args.paths[0]).is_dir()):
            path = Path(args.paths[0])
            if not args.prefix:
                print("Error: --prefix required for directory upload", file=sys.stderr)
                sys.exit(1)
            result = uploader.upload_directory(
                args.paths[0],
                args.prefix,
                pattern=args.pattern,
                recursive=not args.no_recursive,
                sanitize_filenames=args.sanitize,
                quiet=args.quiet,
            )
        elif args.large:
            result = uploader.upload_large_file(
                args.paths[0],
                key=args.key,
                part_size=args.part_size * 1024 * 1024,
                parallel_num=args.parallel,
                enable_checkpoint=not args.no_checkpoint,
                quiet=args.quiet,
            )
        elif args.image:
            # Single image upload
            key_prefix = args.prefix or "statics/i/img"
            path = Path(args.paths[0])
            safe_name = uploader._sanitize_filename(path.name)
            oss_key = args.key or f"{key_prefix}/{safe_name}"
            result = uploader.upload_image(
                args.paths[0], key=oss_key, acl=args.acl or "public-read", quiet=args.quiet
            )
            if result.get("success"):
                result["safe_name"] = safe_name
                result["was_renamed"] = safe_name != path.name

        else:
            result = uploader.upload_file(
                args.paths[0],
                key=args.key,
                content_type=None,
                acl=args.acl,
                storage_class=args.storage_class,
                quiet=args.quiet,
            )
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif result.get("success"):
            # Get actual bucket and region for URL generation
            actual_bucket = result.get('bucket', uploader.bucket)
            actual_region = uploader.region
            if "images" in result:
                # Multi-image upload summary
                print(f"\n✓ 上传完成: {result['success_count']}/{result['total_images']} 张图片")
                print(f"  Bucket: {actual_bucket}")
                print(f"  Region: {actual_region}")
                print(f"  Key 前缀: {result['key_prefix']}")
                print("\n上传结果:")
                for img in result["images"]:
                    if img.get("success"):
                        key = img.get("key", "")
                        name = img.get("original_name", "")
                        url = f"https://{actual_bucket}.oss-{actual_region}.aliyuncs.com/{key}"
                        print(f"  - {url}")
                        print(f"    Key: {key} ({name})")
                    else:
                        print(f"  ✗ {img.get('original_name', 'unknown')}: {img.get('error', 'unknown error')}")
            elif "files" in result:
                # Directory upload summary
                print(
                    f"\n✓ 上传完成: {result['success_count']}/{result['total_files']} 个文件"
                )
                print(f"  Bucket: {actual_bucket}")
                print(f"  Region: {actual_region}")
                print(f"  Total size: {format_size(result['total_size'])}")
                print(f"  Prefix: {result['prefix']}")
                if result.get('sanitize_filenames'):
                    print(f"  文件名处理: 已清理特殊字符")
                print("\n上传结果:")
                for f in result["files"]:
                    if f.get("success"):
                        key = f.get("key", "")
                        original_name = f.get("original_name", "")
                        url = f"https://{actual_bucket}.oss-{actual_region}.aliyuncs.com/{key}"
                        if f.get("was_renamed"):
                            print(f"  - {url}")
                            print(f"    Key: {key} ({original_name} -> {f.get('safe_name', '')})")
                        else:
                            print(f"  - {url}")
                            print(f"    Key: {key}")
                    else:
                        print(f"  ✗ {f.get('original_name', 'unknown')}: {f.get('error', {}).get('message', 'unknown error')}")
            else:
                # Single file
                print(f"\n✓ 上传完成!")
                print(f"  URL: {result['url']}")
                key = result.get('key', '')
                safe_name = result.get('safe_name', '')
                if safe_name:
                    print(f"  Key: {key}")
                    if result.get('was_renamed'):
                        print(f"  (已重命名: {safe_name})")
                else:
                    print(f"  Key: {key}")
                print(f"  Size: {format_size(result['size'])}")
                if result.get("etag"):
                    print(f"  ETag: {result['etag']}")
        else:
            error = result.get("error", {})
            print(
                f"\n✗ Upload failed: [{error.get('code')}] {error.get('message')}",
                file=sys.stderr,
            )
            sys.exit(1)
    except ValueError as e:
        print(f"✗ Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n✗ Upload interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
