#!/bin/bash
#
# Upload files from clipboard
# Usage: 
#   1. Select file(s) in Finder and copy (Cmd+C)
#   2. Run this script
#
# Options:
#   --prefix, -p    OSS key prefix (default: statics/i/img)
#   --bucket, -b    OSS bucket name (or set OSS_BUCKET env var)
#   --images, -i    Upload as images with public-read ACL
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UPLOAD_PY="$SCRIPT_DIR/upload.py"

# Default values
PREFIX="statics/i/img"
BUCKET="${OSS_BUCKET:-}"
MODE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prefix|-p)
            PREFIX="$2"
            shift 2
            ;;
        --bucket|-b)
            BUCKET="$2"
            shift 2
            ;;
        --images|-i)
            MODE="--images"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Upload files from clipboard to OSS."
            echo ""
            echo "Usage:"
            echo "  1. Select file(s) in Finder and copy (Cmd+C)"
            echo "  2. Run this script"
            echo ""
            echo "Options:"
            echo "  --prefix, -p    OSS key prefix (default: statics/i/img)"
            echo "  --bucket, -b    OSS bucket name"
            echo "  --images, -i    Upload as images with public-read ACL"
            echo "  --help, -h      Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: This script only works on macOS"
    exit 1
fi

# Get file paths from clipboard
# Method 1: Try to get as file URLs (alias list)
FILE_PATHS=$(osascript -e 'tell application "Finder" to get POSIX path of (the clipboard as alias list)' 2>/dev/null)

# Method 2: Try HFS file URL format (file VOLUME:path:to:file)
if [[ -z "$FILE_PATHS" ]]; then
    HFS_PATH=$(osascript -e 'the clipboard as «class furl»' 2>/dev/null)
    if [[ -n "$HFS_PATH" ]]; then
        # Convert HFS to POSIX using Python
        FILE_PATHS=$(echo "$HFS_PATH" | python3 -c "
import sys
hfs_path = sys.stdin.read().strip()
if hfs_path.startswith('file '):
    hfs_path = hfs_path[5:]
parts = hfs_path.split(':')
if len(parts) >= 2:
    volume = parts[0]
    rest = '/'.join(parts[1:])
    print(f'/Volumes/{volume}/{rest}')
" 2>/dev/null)
        # Verify file exists
        if [[ -n "$FILE_PATHS" && ! -f "$FILE_PATHS" ]]; then
            FILE_PATHS=""
        fi
    fi
fi

# Method 3: Try as text (might be paths copied as text)
if [[ -z "$FILE_PATHS" ]]; then
    CLIPBOARD_TEXT=$(pbpaste 2>/dev/null)
    # Check if clipboard contains valid file paths
    VALID_PATHS=""
    while IFS= read -r line; do
        # Expand ~ and check if file exists
        EXPANDED=$(eval echo "$line" 2>/dev/null)
        if [[ -f "$EXPANDED" ]]; then
            if [[ -n "$VALID_PATHS" ]]; then
                VALID_PATHS="$VALID_PATHS"$'\n'"$EXPANDED"
            else
                VALID_PATHS="$EXPANDED"
            fi
        fi
    done <<< "$CLIPBOARD_TEXT"
    FILE_PATHS="$VALID_PATHS"
fi

if [[ -z "$FILE_PATHS" ]]; then
    echo "Error: No valid file paths found in clipboard"
    echo ""
    echo "Please:"
    echo "  1. Select file(s) in Finder"
    echo "  2. Copy (Cmd+C)"
    echo "  3. Run this script again"
    echo ""
    echo "Or copy file paths as text, one per line"
    exit 1
fi

# Convert AppleScript list format to space-separated paths
# AppleScript returns: path1, path2, path3
FILE_PATHS=$(echo "$FILE_PATHS" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$' | tr '\n' ' ' | sed 's/ $//')

echo "Files to upload:"
echo "$FILE_PATHS" | tr ' ' '\n' | while read -r path; do
    echo "  - $path"
done
echo ""

# Build command
CMD="python3 \"$UPLOAD_PY\" $FILE_PATHS --prefix \"$PREFIX\""

if [[ -n "$BUCKET" ]]; then
    CMD="$CMD --bucket \"$BUCKET\""
fi

if [[ -n "$MODE" ]]; then
    CMD="$CMD $MODE"
fi

# Execute upload
eval $CMD
