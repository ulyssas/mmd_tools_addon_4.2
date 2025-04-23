# MMD Tools Developer Guide

This guide helps both new and experienced contributors understand MMD Tools’ goals, structure, and recommended practices.
Please read it carefully before submitting ideas or pull requests.

## Project Scope

### Core Principles
- **MMD Compatibility**: MMD Tools preserves official MikuMikuDance (MMD) file formats for models, motions, and poses
- **User-Friendly Workflow**: By focusing on MMD-compatible features, MMD Tools provides a straightforward, efficient experience for MMD users within Blender
- **Non-Breaking Enhancements**: Only improvements and tools that do not break the MMD format integrity are added

### Supported Features
1. **Import/Export** - Read and write MMD formats without altering the MMD file formats
2. **Editing** - Support editing and modifying MMD data in Blender while preserving MMD compatibility
3. **Verification** - Preview and confirm MMD-compliant physics, motions, and other features directly in Blender

### Out of Scope
1. **MMD Format Changes** - Any modification that breaks official MMD specifications or compatibility
2. **Extended Functionality** - Features that significantly exceed MMD’s scope—such as advanced rigging or shader systems specialized for high-end movie production—should be developed as separate add-ons
3. **Third-Party Incorporations** - Support for non-MMD workflows or custom file formats

## Development Environment

### Prerequisites
- Ensure you have a matching version of Blender for the target development branch
- Use the correct Python version for your Blender release
- Get GitHub access to the [MMD Tools repository](https://github.com/MMD-Blender/blender_mmd_tools)

| Blender Version | MMD Tools Version | Python Version | Branch                                                                         |
|-----------------|-------------------|---------------:|--------------------------------------------------------------------------------|
| Blender 4.2 LTS | MMD Tools v4.x    |           3.11 | [main](https://github.com/MMD-Blender/blender_mmd_tools)                       |
| Blender 3.6 LTS | MMD Tools v2.x    |           3.10 | [blender-v3](https://github.com/MMD-Blender/blender_mmd_tools/tree/blender-v3) |

### Recommendations
- Use a dedicated Python virtual environment for development
- Use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Use [fake-bpy-module](https://github.com/nutti/fake-bpy-module) for code completion and type checking in IDEs

## Project Structure
```
blender_mmd_tools/
├── mmd_tools/         # Main module directory
│   ├── core/          # Core functionality
│   ├── operators/     # Blender operators
│   ├── panels/        # Blender UI panels
│   ├── properties/    # Blender Property definitions
│   ├── externals/     # Dependent 3rd-party modules with README.txt
│   └── typings/       # Python Type Hints (.pyi)
└── docs/              # Documentation (not yet)
```

## Coding Standards

### Python Style
- Use [Ruff’s default style](https://docs.astral.sh/ruff/formatter/#philosophy) for linting and formatting
- Keep line length under 256 characters (`--line-length=256`)
- Indent with 4 spaces (no tabs)
- Add the following comment block at the top of each Python file:
  ```
  # -*- coding: utf-8 -*-
  # Copyright {year} MMD Tools authors
  # This file is part of MMD Tools.
  ```

### Naming Conventions
- Follow Ruff’s conventions for classes, functions, variables, and constants

### Comments and Documentation
- Write docstrings for public functions, classes, and modules
- Provide clear comments for complex logic
- Keep docstrings and documentation updated as the code evolves

## Git Workflow (GitHub Flow)
We adopt [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow) for a simple, flexible development process:

1. Create a branch from `main`:
   ```
   git checkout -b feature/your-feature
   ```
2. Make your changes in small, focused commits
3. Write meaningful commit messages:
   ```
   [Component] Short description
   ...
   ```
4. Push your branch to your fork
5. Open a pull request against `main`
6. Merge your pull request once it’s approved

### Translating the Extension
This section explains some details on the workflow of translating this extension, which is supported by the Blender [Manage UI translations](https://developer.blender.org/docs/handbook/translating/translator_guide/#manage-ui-translations-add-on) official extension. 
If you want to modify only the translated strings, you can ignore this section and directly edit the `m17n.py` files.
This workflow is only needed when new UI elements/operators are added to this extension to extract new translatable strings.

To use this extension, you need first to set up its environment:
1. Enable the extension, along with the MMD Tools, from the Blender Perferences interface. It is bundled with Blender, so you don't need to install it seperately.
2. Set up localization resources for the extension. First, clone the repositories needed:
   ```
   git clone --depth 1 https://github.com/blender/blender
   git clone --depth 1 https://projects.blender.org/blender/blender-ui-translations
   ```
   These repositories are mandatory for the extension to function normally, but we will not modify them.
3. Then configure the extension. In the Preferences window of the Manage UI translations extension, point `Source Root` to the root of the former repository (where `.git` is located, not its subdirectories), and `Translation Root` to the root of the latter. Note that these configurations are not persistent unless saved explicitly and could revert to previous ones on each Blender restart.
4. Check whether it is functional. On the Render properties section of the scene editor (where you can switch between EEVEE and Cycles engines), you should be able to find an `I18n Update Translation` panel, and it should be similar to the one you can find on [this page](https://developer.blender.org/docs/handbook/translating/translator_guide/#manage-ui-translations-add-on).

After setting up the environment, first click the `Refresh i18n data` button.
Then, you can use the `Export PO...` button to generate `.po` files used for translation. 
This should generate text files that can be edited by any text editor for translation.
After finishing, click the `Import PO...` button to update the interface and the Python source code.
This should update the `m17n.py` located at the root of this extension.

If clicking the `Refresh i18n data` resulted in errors like:
```
KeyError: 'bpy_prop_collection[key]: key "Blender_27x" not found'
```
You can try to load the specified key binding preset from the Preferences window and retry.
This is likely an upstream issue that can only be resolved by the Blender developers.

## Release Process
Currently, only @UuuNyaa has permission to perform release tasks:

1. Tag the commit in `main` with the version number (`vMAJOR.MINOR.PATCH`)
2. Pushing the tag triggers a GitHub Action that builds artifacts and creates a draft release
3. Manually finalize and publish the GitHub Release draft
4. Manually upload the artifacts to [Blender Extensions](https://extensions.blender.org/add-ons/mmd-tools/)

## Getting Help
If you need help with development:
- Ask questions in the [MMD & Blender Discord Server](https://discord.gg/zRgUkuaPWw) `#addon-development` channel
- Open an issue to discuss implementation details
- Refer to existing code for patterns and approaches

We appreciate your contributions and look forward to working together to improve MMD Tools!
