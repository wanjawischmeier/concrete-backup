#!/bin/bash

# Create Debian package structure for concrete-backup
# Usage: create-deb-structure.sh <version> <deb_dir>

VERSION="$1"
DEB_DIR="$2"
PACKAGE_NAME="concrete-backup"

if [ -z "$VERSION" ] || [ -z "$DEB_DIR" ]; then
    echo "Usage: $0 <version> <deb_dir>"
    exit 1
fi

# Create directory structure
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/pixmaps"
mkdir -p "$DEB_DIR/usr/share/doc/$PACKAGE_NAME"
mkdir -p "$DEB_DIR/opt/$PACKAGE_NAME"

# Copy the PyInstaller executable
if [ -f "dist/concrete-backup-bin" ]; then
    cp dist/concrete-backup-bin "$DEB_DIR/opt/$PACKAGE_NAME/concrete-backup-bin"
    chmod +x "$DEB_DIR/opt/$PACKAGE_NAME/concrete-backup-bin"
else
    echo "Error: dist/concrete-backup-bin not found"
    exit 1
fi

# Copy the launcher script
cp .github/scripts/launcher-script.sh "$DEB_DIR/usr/bin/$PACKAGE_NAME"
chmod +x "$DEB_DIR/usr/bin/$PACKAGE_NAME"

# Copy desktop entry
cp .github/scripts/concrete-backup.desktop "$DEB_DIR/usr/share/applications/$PACKAGE_NAME.desktop"

# Copy icon - use icon.png if available, otherwise create a simple placeholder
if [ -f "icon.png" ]; then
    cp icon.png "$DEB_DIR/usr/share/pixmaps/$PACKAGE_NAME.png"
    echo "Using project icon.png"
else
    echo "Warning: icon.png not found in project directory, creating placeholder"
    # Create a simple 32x32 blue square as placeholder
    convert -size 32x32 xc:"#0078D4" "$DEB_DIR/usr/share/pixmaps/$PACKAGE_NAME.png" 2>/dev/null || {
        echo "ImageMagick not available, creating XPM fallback"
        cat > "$DEB_DIR/usr/share/pixmaps/$PACKAGE_NAME.xpm" << 'EOF'
/* XPM */
static char * concrete_backup_xpm[] = {
"32 32 2 1",
" 	c None",
".	c #0078D4",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................"};
EOF
    }
fi

# Create copyright file
sed "s/YEAR/$(date +%Y)/g" .github/scripts/copyright.template > "$DEB_DIR/usr/share/doc/$PACKAGE_NAME/copyright"

# Create changelog
sed -e "s/VERSION/$VERSION/g" -e "s/DATE/$(date -R)/g" .github/scripts/changelog.template > "$DEB_DIR/usr/share/doc/$PACKAGE_NAME/changelog.Debian"
gzip -9 "$DEB_DIR/usr/share/doc/$PACKAGE_NAME/changelog.Debian"

# Create control file
INSTALLED_SIZE=$(du -s "$DEB_DIR" | cut -f1)
sed -e "s/VERSION/$VERSION/g" -e "s/INSTALLED_SIZE/$INSTALLED_SIZE/g" .github/scripts/control.template > "$DEB_DIR/DEBIAN/control"

# Copy prerm script
cp .github/scripts/prerm.sh "$DEB_DIR/DEBIAN/prerm"
chmod +x "$DEB_DIR/DEBIAN/prerm"

echo "Debian package structure created successfully in $DEB_DIR"
