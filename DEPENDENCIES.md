# Dependencies - Latest Stable Versions

This document tracks the latest stable versions of all dependencies used in the Driver Scheduling System.

## Desktop Application (Node.js/Electron)

### Core Dependencies
- **Electron**: `^39.2.4` (Latest stable as of December 2024)
- **React**: `^19.2.0` (Latest stable as of December 2024)
- **React DOM**: `^19.2.0` (Latest stable as of December 2024)

### Development Dependencies
- **electron-builder**: `^26.0.12` (Latest stable as of December 2024)

### Installation
```bash
cd desktop
npm install
```

## ETL Module (Python)

### Core Dependencies
- **pandas**: `>=2.2.3` (Latest stable as of December 2024)
- **numpy**: `>=2.1.0` (Latest stable as of December 2024)

### Installation
```bash
cd etl
pip install -r requirements.txt
```

## Version Update Notes

### December 2024
- Updated Electron from 28.0.0 to 39.2.4
- Updated electron-builder from 24.9.1 to 26.0.12
- Updated React from 18.2.0 to 19.2.0
- Updated React DOM from 18.2.0 to 19.2.0
- Updated pandas minimum version to 2.2.3
- Updated numpy minimum version to 2.1.0

## Notes

- **React 19**: This is a major version update with potential breaking changes. If you encounter compatibility issues, consider downgrading to React 18.3.1.
- **Electron 39**: Includes Node.js v22.20.0 and Chromium M142.
- All versions use caret (^) ranges for Node.js packages to allow patch and minor updates while maintaining compatibility.

## Updating Dependencies

To check for updates:
```bash
# Node.js packages
cd desktop
npm outdated

# Python packages
cd etl
pip list --outdated
```

To update to latest versions:
```bash
# Node.js packages
cd desktop
npm update

# Python packages
cd etl
pip install --upgrade -r requirements.txt
```

