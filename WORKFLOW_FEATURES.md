# GitHub Actions Workflow Features

## Version-Aware Artifacts

The workflow automatically:

1. **Extracts version** from `pyproject.toml` using `poetry version --short`
2. **Names artifacts with version**:
   - `concrete-backup-{version}-linux` (standalone executable)
   - `concrete-backup-{version}-bundle-linux` (complete bundle)
3. **Names the executable** with version: `concrete-backup-{version}`

## Automatic Release Creation

The workflow creates GitHub releases automatically when:

- Code is pushed to `main` branch
- A version tag is pushed (e.g., `v0.1.0`)

### Release Features:

- **Checks if release exists** before creating (no duplicates)
- **Creates release archives**:
  - `concrete-backup-{version}-linux-x86_64.tar.gz`
  - `concrete-backup-{version}-bundle-linux-x86_64.tar.gz`
- **Generates release notes** with download links and installation instructions
- **Uses semantic versioning** tags (e.g., `v0.1.0`)

## Manual Release Creation

To create a release manually:

```bash
# Update version in pyproject.toml
poetry version 0.2.0

# Commit the version change
git add pyproject.toml
git commit -m "Bump version to 0.2.0"

# Create and push a tag
git tag v0.2.0
git push origin main --tags
```

This will trigger the workflow and automatically create a release with the new version.

## Artifact Naming Examples

For version `0.1.0`:
- Artifact: `concrete-backup-0.1.0-linux`
- Bundle: `concrete-backup-0.1.0-bundle-linux`
- Release files:
  - `concrete-backup-0.1.0-linux-x86_64.tar.gz`
  - `concrete-backup-0.1.0-bundle-linux-x86_64.tar.gz`
