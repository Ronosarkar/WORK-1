#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=== Installing Python Dependencies ==="
pip install --upgrade pip
pip install -r requirements-server.txt

echo "=== Setting up Linux FFmpeg & FFprobe ==="
mkdir -p bin

# If ffmpeg is already in system PATH, we don't need to download
if command -v ffmpeg &> /dev/null; then
    echo "FFmpeg is already installed in system PATH!"
else
    echo "Downloading portable static FFmpeg for Linux..."
    # Download static John Van Sickle or GitHub Linux 64-bit release
    curl -sL https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz || \
    curl -sL https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/linux-x64 -o bin/ffmpeg
    
    if [ -f "ffmpeg.tar.xz" ]; then
        tar -xJf ffmpeg.tar.xz --wildcards '*/ffmpeg' '*/ffprobe' --strip-components=1 -C bin/
        rm -f ffmpeg.tar.xz
    fi
    chmod +x bin/ffmpeg bin/ffprobe 2>/dev/null || true
fi

echo "=== Build Complete ==="
