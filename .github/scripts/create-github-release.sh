#!/bin/bash

# Create GitHub release
# Usage: create-github-release.sh <version>

VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

# Create release notes
cat > release-notes.md << EOF
# Concrete Backup v$VERSION

Automated release for version $VERSION.

## Downloads

- **concrete-backup_${VERSION}-1_amd64.deb**: Debian package for Ubuntu/Debian systems with full desktop integration

## Installation

### Ubuntu/Debian:
1. Download the .deb package
2. Install: \`sudo dpkg -i concrete-backup_${VERSION}-1_amd64.deb\`
3. If dependencies are missing: \`sudo apt-get install -f\`
4. Launch from applications menu or run \`concrete-backup\` in terminal

## Features

- **Desktop Integration**: Appears in applications menu with proper icon
- **Privilege Escalation**: Automatically prompts for password when elevated access is needed
- **Graphical Interface**: Full PyQt5-based GUI for backup configuration
- **Scheduled Backups**: Cron integration for automated backups
- **Multiple Destinations**: Support for various backup targets

## System Requirements

- Ubuntu 18.04+ or Debian 10+
- X11 or Wayland desktop environment
- PolicyKit for privilege escalation (usually pre-installed)
- No Python dependencies required (self-contained executable)
EOF

# Create the release
gh release create "v$VERSION" \
  --title "Concrete Backup v$VERSION" \
  --notes-file release-notes.md \
  release-files/concrete-backup_${VERSION}-1_amd64.deb
