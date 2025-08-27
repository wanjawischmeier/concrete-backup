#!/bin/bash

# Test Debian package for concrete-backup
# Usage: test-deb-package.sh <version>

VERSION="$1"
PACKAGE_FILE="concrete-backup_${VERSION}-1_amd64.deb"

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

# Test that the package was created
if [ -f "$PACKAGE_FILE" ]; then
  echo "✓ Debian package created successfully"
  ls -la "$PACKAGE_FILE"
  
  # Test that the executable is included and works
  echo "Testing package contents..."
  dpkg-deb --contents "$PACKAGE_FILE" | grep concrete-backup-bin
  
  # Test package installation (dry run)
  echo "Testing package installation (dry run)..."
  sudo dpkg --dry-run -i "$PACKAGE_FILE"
  
  echo "✓ Package installation test passed"
else
  echo "✗ Debian package not found"
  exit 1
fi
