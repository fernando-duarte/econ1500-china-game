# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-11-08

### Added
- Centralized version management system with version-management.js
- Comprehensive version management documentation
- Scripts for version updates and validation:
  - scripts/update-versions.js: Updates versions across all files
  - scripts/generate-python-locks.sh: Generates requirements.lock files
  - scripts/validate-versions.js: Validates version consistency
- GitHub Actions workflow for automated version validation

### Changed
- Standardized Python version to 3.12.2 across all components
- Updated Node.js to 20.13.1 to match specifications
- Standardized FastAPI to 0.110.0 and Pandas to 2.2.2
- Normalized Docker image naming across dev and prod environments
- Improved consistency in volume naming conventions
- Consolidated Python requirements lock generation into a single script

### Fixed
- Resolved version inconsistencies between specs and implementation
- Fixed socket.io version mismatch between client and server
- Corrected Docker base image versions

### Reverts
- Reverted FastAPI from 0.115.12 to 0.110.0 for compatibility with specs
- Reverted Pandas from 2.2.3 to 2.2.2 to match specifications
- Reverted Pydantic to 2.6.3 for compatibility with FastAPI 0.110.0
- Standardized on Python dotenv 1.0.1 instead of 1.1.0
- Reverted Typing-extensions from 4.13.2 to 4.10.0

### Security
- Maintained exact version pinning for all dependencies
- Ensured all dependencies are compatible with standardized versions

### Compatibility
- Ensured cross-compatibility between all components
- Maintained NumPy at 1.26.4 for stability

## [1.1.0] - 2024-06-01

### Added
- Centralized version management system
- Version update process documentation
- Script to automatically generate requirements.lock

### Changed
- Standardized Python version to 3.12.2 across all components
- Updated Node.js to 20.13.1 to match specifications
- Standardized FastAPI to 0.110.0 and Pandas to 2.2.2
- Normalized Docker image naming across dev and prod environments
- Improved consistency in volume naming conventions

### Fixed
- Resolved version inconsistencies between specs and implementation
- Fixed socket.io version mismatch between client and server
- Corrected Docker base image versions

### Updated
- Updated Node.js from 20.10.0 to 20.12.1 (LTS)
- Updated FastAPI from 0.100.0 to 0.110.0
- Updated Uvicorn from 0.27.1 to 0.34.1
- Updated Pydantic from 2.6.3 to 2.11.3
- Updated Pandas from 2.2.2 to 2.2.3
- Updated Matplotlib from 3.8.3 to 3.9.4
- Updated Python-dotenv from 1.0.1 to 1.1.0
- Updated Typing-extensions from 4.10.0 to 4.13.2

### Security
- Fixed potential security vulnerabilities in dependencies
- Maintained exact version pinning for all dependencies

### Compatibility
- Ensured cross-compatibility between all components
- Maintained NumPy at 1.26.4 for stability (not upgrading to 2.0.x yet)

## [1.0.0] - 2024-05-15

### Added
- Initial release of China Growth Game
- Implemented Solow growth model simulation
- Created React frontend with Material UI
- Developed Node.js/Express backend
- Built Python/FastAPI economic model
- Added Docker containerization
- Implemented security best practices
