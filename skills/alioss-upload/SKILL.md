---
name: alioss-upload
description: Upload files and directories to Alibaba Cloud OSS using Python SDK v2. Supports single file upload, multiple image upload with auto-renaming, batch directory upload, and large file resumable upload. Use when users request "upload to OSS", "阿里云OSS上传", "upload images", "批量上传图片", or any file upload task involving Alibaba Cloud OSS.
---

# OSS Upload

Upload files and directories to Alibaba Cloud Object Storage Service (OSS) using Python SDK v2.

## Configure Environment Variables

[Get Access Key](https://ram.console.aliyun.com/manage/ak)

```bash
# 在 shell 配置文件中设置 (~/.zshrc, ~/.bashrc, 或 ~/.config/fish/config.fish)
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export OSS_REGION="cn-hangzhou"           # 可选, 默认: cn-hangzhou
export OSS_BUCKET="your-bucket-name"      # 可选, 也可通过 --bucket 参数传递

# 使环境变量生效 (二选一)
source ~/.zshrc  # 或 source ~/.bashrc
```

**Note**: Environment variables must be set in your shell configuration. The script reads from `os.environ`, so it works automatically when variables are exported in your shell.

## Output Behavior (Important)

**After upload succeeds, display the OSS URL directly to the user!**

When upload completes, output in this format:

```markdown
✓ Upload complete!
  URL: https://bucket.oss-region.aliyuncs.com/path/to/file
  Key: path/to/file
  Size: 1.5 MB
  ETag: "abc123..."
```

For images uploaded with `--image`, the URL is publicly accessible.

## Quick Start

### Install Dependency

```bash
pip install alibabacloud-oss-v2
```

**Important**: 
- Ensure the SDK is installed in the same Python environment that will run the script
- If you see "ModuleNotFoundError", check which Python is being used: `which python3`
- You may need to install to a specific Python: `/Library/Frameworks/Python.framework/Versions/3.10/bin/python3 -m pip install alibabacloud-oss-v2`

### Upload Single File

```bash
# Basic upload
scripts/upload.py file.txt --bucket my-bucket

# Upload with custom key (path in bucket)
scripts/upload.py photo.jpg --key images/2024/photo.jpg --bucket my-bucket

# Upload with public-read access
scripts/upload.py document.pdf --bucket my-bucket --acl public-read
```

### Upload Image (Public URL)

```bash
# Quick image upload with public-read ACL
scripts/upload.py photo.jpg --bucket my-bucket --image

# Output: https://my-bucket.oss-cn-hangzhou.aliyuncs.com/photo.jpg
```

### Interactive Input (No Paths Required)

When no file paths are provided via command line, the script will prompt for input:

```bash
# Run without paths - will prompt interactively
scripts/upload.py --images --bucket my-bucket

# Interactive prompt example:
# Enter file paths to upload (one per line, empty line to finish):
#   Supported formats:
#     - Plain path: /Users/me/photo.jpg
#     - Path with spaces: /Users/me/My Photos/photo.jpg
#     - file:// URL: file:///Users/me/photo.jpg
#     - Home directory: ~/Desktop/photo.png
#   Or paste multiple paths (one per line):
# --------------------------------------------------
# /Users/me/Desktop/photo1.jpg
# /Users/me/My Photos/photo2.png
# ~/Downloads/screenshot.png
# file:///Users/me/Desktop/live-2746.png
#
# (press Enter on empty line to start upload)
```

**Supported Input Formats:**
- Plain paths: `/Users/me/photo.jpg`
- Paths with spaces: `/Users/me/My Photos/photo.jpg`
- file:// URLs: `file:///Users/me/photo.jpg` (automatically converted to local path)
- Home directory: `~/Desktop/photo.png` (tilde expansion)
- Environment variables: `$HOME/Desktop/photo.png` (expanded automatically)

**Path Validation:**
- Invalid paths are automatically filtered out with warnings
- Duplicates are removed
- Paths are normalized and resolved to absolute paths

### Stdin Pipe Input

```bash
# Pipe file paths via stdin
echo "/path/to/file1.jpg /path/to/file2.png" | scripts/upload.py --images --bucket my-bucket

# Or from a file containing paths
cat file_list.txt | scripts/upload.py --images --bucket my-bucket
```

### Upload Multiple Images (推荐)

批量上传多张图片，自动处理中文/特殊字符文件名:

```bash
# 上传多张图片 (默认 key 前缀: statics/i/img)
scripts/upload.py img1.jpg img2.png photo.jpg --images --bucket my-bucket

# 自定义 key 前缀
scripts/upload.py photo1.jpg "照片.jpg" banner.png --images --bucket my-bucket --prefix assets/img

# 输出格式:
# ✓ 上传完成: 3/3 张图片
#   Key 前缀: statics/i/img
#
# 上传结果:
#   - statics/i/img/photo1.jpg (photo1.jpg)
#   - statics/i/img/a1b2c3d4e5f6.jpg (照片.jpg)  # 自动重命名
#   - statics/i/img/banner.png (banner.png)
```

**特性:**
- 中文/特殊字符文件名自动重命名为安全的 MD5 哈希名
- 保持原始文件扩展名
- 默认公开访问 (public-read)
- 返回 `key + 原始文件名` 格式

### Upload Directory

```bash
# Upload all files in directory
scripts/upload.py ./images --prefix assets/images --bucket my-bucket --dir

# Upload only JPG files
scripts/upload.py ./photos --prefix photos --bucket my-bucket --dir --pattern "*.jpg"

# Non-recursive (skip subdirectories)
scripts/upload.py ./assets --prefix assets --bucket my-bucket --dir --no-recursive
```

### Upload Large File (Resumable)

```bash
# Large file with automatic multipart and resumable upload
scripts/upload.py video.mp4 --bucket my-bucket --large

# Custom part size and parallelism
scripts/upload.py big-data.zip --bucket my-bucket --large --part-size 10 --parallel 5
```

## Command-Line Options

```
scripts/upload.py PATHS [OPTIONS]
Arguments:
  PATHS                 Local file or directory paths to upload (supports multiple)
Required (one of):
  --bucket, -b          OSS bucket name (or set OSS_BUCKET env var)
  --prefix, -p          OSS key prefix (default for images: statics/i/img)
Upload Modes (mutually exclusive):
  --large, -l           Use multipart upload for large files (with resumable)
  --image, -i           Upload single image with public access
  --images              Upload multiple images (auto-sanitize filenames)
  --dir, -d             Upload directory contents

Options:
  --key, -k             OSS object key (default: filename)
  --region, -r          OSS region (default: cn-hangzhou)
  --acl                 Object ACL: private, public-read, public-read-write
  --storage-class       Storage class: Standard, IA, Archive
  --pattern             File pattern for directory upload (default: *)
  --no-recursive        Don't include subdirectories
  --part-size           Part size in MB for large files (default: 6)
  --parallel            Parallel uploads for large files (default: 3)
  --no-checkpoint       Disable resumable upload

Output:
  --quiet, -q           Suppress progress output
  --json                Output raw JSON response

Environment Variables:
  OSS_ACCESS_KEY_ID       Access Key ID (required)
  OSS_ACCESS_KEY_SECRET   Access Key Secret (required)
  OSS_REGION              Region (default: cn-hangzhou)
  OSS_BUCKET              Default bucket name
  OSS_CHECKPOINT_DIR      Checkpoint directory for resumable uploads
```

## Upload Scenarios

### 1. Upload Website Assets

```bash
# Upload static assets to OSS
scripts/upload.py ./dist --prefix static --bucket my-web-bucket --dir
```

### 2. Upload Log Files to Archive

```bash
# Upload to Archive storage class for cost savings
scripts/upload.py logs.tar.gz --bucket archive-bucket --storage-class Archive
```

### 3. Upload User-Generated Images

```bash
# Batch upload with pattern
scripts/upload.py ./uploads --prefix user-content/2024 --bucket media-bucket --dir --pattern "*.jpg"
```

### 4. Upload Large Video Files

```bash
# Resumable upload for large files (handles network interruptions)
scripts/upload.py ./videos/webinar.mp4 --bucket video-bucket --large --key videos/2024/webinar.mp4
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `NoSuchBucket` | Bucket doesn't exist | Create bucket in OSS console |
| `AccessDenied` | Invalid credentials or permissions | Check Access Key and bucket ACL |
| `EntityTooLarge` | File exceeds 5GB limit | Use `--large` for multipart upload |
| `InvalidAccessKeyId` | Wrong Access Key ID | Verify OSS_ACCESS_KEY_ID |
| `SignatureDoesNotMatch` | Wrong Secret Key | Verify OSS_ACCESS_KEY_SECRET |

## OSS URL Format

Uploaded files are accessible at:

```
https://{bucket}.oss-{region}.aliyuncs.com/{key}
```

Example:
```
https://my-bucket.oss-cn-hangzhou.aliyuncs.com/images/photo.jpg
```

## Storage Classes

| Class | Use Case | Price |
|-------|----------|-------|
| Standard | Frequent access | Highest |
| IA (Infrequent Access) | Rare access, 30-day min | Lower |
| Archive | Long-term archival, 60-day min | Lowest |

## Reference Documentation

- [OSS Python SDK v2 Developer Guide](https://www.alibabacloud.com/help/en/oss/developer-reference/overview-of-oss-sdk-for-python-v2)
- [OSS Console](https://oss.console.aliyun.com/)
- [RAM Access Key Management](https://ram.console.aliyun.com/manage/ak)
- [OSS Regions and Endpoints](https://www.alibabacloud.com/help/en/oss/user-guide/regions-and-endpoints)
