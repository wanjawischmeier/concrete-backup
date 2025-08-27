#!/bin/bash

# Build and test Debian package for concrete-backup
# Usage: build-deb-package.sh <version>

VERSION="$1"
DEB_DIR="debian-package"

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

# Build the package
dpkg-deb --build "$DEB_DIR" "concrete-backup_${VERSION}-1_amd64.deb"

# Verify the package
echo "Package contents:"
dpkg-deb --contents "concrete-backup_${VERSION}-1_amd64.deb"

echo "Package info:"
dpkg-deb --info "concrete-backup_${VERSION}-1_amd64.deb"
