#!/bin/bash

# Create release archive and files
# Usage: create-release-archive.sh <version>

VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

# Create release files directory
mkdir -p release-files

# Copy all package formats if they exist
if find artifacts/ -name "*.deb" -type f | head -1 > /dev/null 2>&1; then
    echo "Copying Debian packages..."
    cp artifacts/*.deb release-files/
fi

if find artifacts/ -name "*.rpm" -type f | head -1 > /dev/null 2>&1; then
    echo "Copying RPM packages..."
    cp artifacts/*.rpm release-files/
fi

if find artifacts/ -name "*.tar.gz" -type f | head -1 > /dev/null 2>&1; then
    echo "Copying source archives..."
    cp artifacts/*.tar.gz release-files/
fi

echo "Release archive created in release-files/"
echo "Available packages:"
ls -la release-files/
