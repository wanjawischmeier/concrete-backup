#!/bin/bash

# Create release archive and files
# Usage: create-release-archive.sh <version>

VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

# Create Debian package archive
mkdir -p release-files
cp artifacts/concrete-backup_${VERSION}-1_amd64.deb release-files/

echo "Release archive created in release-files/"
