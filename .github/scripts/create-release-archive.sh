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

# Copy Debian package
if find artifacts/ -name "*.deb" -type f | head -1 > /dev/null 2>&1; then
    echo "Copying Debian package..."
    cp artifacts/*.deb release-files/
else
    echo "Warning: No Debian package found in artifacts/"
fi

echo "Release archive created in release-files/"
echo "Available packages:"
ls -la release-files/
