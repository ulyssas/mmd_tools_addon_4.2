# MMD Tools Developer Guide

This guide is meant to help new and experienced contributors understand MMD Tools’ goals, structure, and recommended practices. Please read it carefully before submitting ideas or pull requests.

## Project Scope

### Core Principles
- Focus on MikuMikuDance (MMD) compatibility
- Provide a seamless and user-friendly workflow between Blender and MMD
- Preserve format integrity for models, motions, and poses
- For functionality beyond MMD Tools’ scope, create separate add-ons instead of modifying MMD Tools

### Supported Features
1. **Import/Export** - Complete support for MMD file formats
2. **Editing** - Tools to modify MMD assets within Blender
3. **Compatibility** - Support for all standard MMD features
4. **Verification** - Preview and validation features (e.g. Physics) for MMD compatibility

### Out of Scope
1. **Extended Functionality** - Features beyond MMD capabilities
2. **Format Modifications** - Changes that break MMD compatibility
3. **Non-Standard Extensions** - Additions not supported by MMD

## Development Environment

### Prerequisites
- Ensure Blender is installed and matches the target branch version
- Use the correct Python version for your Blender release
- Ensure GitHub access to the [repository](https://github.com/MMD-Blender/blender_mmd_tools)

| Blender Version | MMD Tools Version | Python Version | Branch      |
|-----------------|-------------------|---------------:|-------------|
| Blender 4.2 LTS | MMD Tools v4.x    |           3.11 | [main](https://github.com/MMD-Blender/blender_mmd_tools) |
| Blender 3.6 LTS | MMD Tools v2.x    |           3.10 | [blender-v3](https://github.com/MMD-Blender/blender_mmd_tools/tree/blender-v3) |

### Recommendations
- Use a dedicated Python virtual environment for development
- Use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Use [fake-bpy-module](https://github.com/nutti/fake-bpy-module) for the code completion and type checking in IDEs

## Project Structure
```
blender_mmd_tools/
├── mmd_tools/            # Main module directory
│   ├── core/             # Core functionality 
│   ├── operators/        # Blender operators
│   ├── panels/           # Blender UI panels
│   ├── properties/       # Blender Property definitions
│   ├── externals/        # Dependent 3rd-party modules with README.txt
│   └── typings/          # Python Type Hints (.pyi)
└── docs/                 # Documentation (not yet)
```

## Coding Standards

### Python Style
- Use [Ruff’s default style](https://docs.astral.sh/ruff/formatter/#philosophy) configuration for linting and formatting
- Keep line length under 256 characters (`--line-length=256`)
- Continue using 4 spaces for indentation (not tabs)
- Add the following at the top of each Python file:
    ```
    # -*- coding: utf-8 -*-
    # Copyright {year} MMD Tools authors
    # This file is part of MMD Tools.
   ```

### Naming Conventions
- Follow Ruff’s recommended naming style for classes, functions, variables, and constants

### Comments and Documentation
- Write docstrings for all functions, classes, and modules
- Write clear comments for complex logic
- Maintain up-to-date docstrings and documentation


## Git Workflow (GitHub flow)
We adopt [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow) to keep the development process simple and straightforward.

1. Create a branch from `main`:
   ```
   git checkout -b feature/your-feature
   ```
2. Make your changes with small, focused commits
3. Write meaningful commit messages:
   ```
   [Component] Short description
   ...
   ```
4. Push your branch to your fork
5. Open a pull request against `main`
6. Merge your pull request once approved


## Release Process

Currently, only @UuuNyaa has permission to perform release tasks.

1. Add a version tag (`vMAJOR.MINOR.PATCH`) to the commit targeted for release in `main` branch
2. When you push the version tag, GitHub Actions automatically builds artifacts and creates a GitHub Release Draft
3. Manually finish the GitHub Release Draft and publish it
4. Manually upload the artifacts to [Blender Extensions](https://extensions.blender.org/add-ons/mmd-tools/)

## Getting Help

If you need help with development:

- Ask questions in the [MMD & Blender Discord Server](https://discord.gg/zRgUkuaPWw) `#addon-development` channel
- Open an issue for discussing implementation details
- Check existing code for patterns and approaches

We appreciate your contributions and look forward to working together to improve MMD Tools!
