# Test Runner

## Running All Tests

The test runner supports three launch methods:

```
# Method 1: From Blender
blender --background -noaudio --python tests/all_test_runner.py -- --verbose

# Method 2: With Python (using PATH)
python all_test_runner.py

# Method 3: With Python (explicit path)
python all_test_runner.py "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
```

If any tests FAIL, run the individual test file to see detailed error information.

## Running Individual Tests

Run individual test scripts directly:
```
blender --background -noaudio --python tests/test_pmx_exporter.py -- --verbose
blender --background -noaudio --python tests/test_vmd_exporter.py -- --verbose
...
```

## Available Test Scripts

Check the tests folder in the repo.

## Test Coverage
```
C:.
|   ✗ auto_load.py
|   ✗ auto_scene_setup.py
|   - blender_manifest.toml
|   ✗ bpyutils.py
|   ✗ cycles_converter.py
|   ✗ handlers.py
|   ✗ m17n.py
|   ✗ menus.py
|   ✗ preferences.py
|   ✗ translations.py
|   ✓ utils.py (test_utils_unit.py)
|   - __init__.py
|
+---core
|   |   ✓ bone.py (test_bone.py)
|   |   ✓ camera.py (test_camera_system.py)
|   |   ✗ exceptions.py
|   |   ✓ lamp.py (test_lamp_system.py)
|   |   ✓ material.py (test_material_system.py)
|   |   ✓ model.py (used in multiple test files)
|   |   ✓ morph.py (test_morph_system.py)
|   |   ✓ rigid_body.py (test_rigid_body.py)
|   |   ✓ sdef.py (test_sdef_system.py)
|   |   ✓ shader.py (test_material_system.py)
|   |   ✗ translations.py
|   |   - __init__.py
|   |
|   +---pmd
|   |       ✓ importer.py (used in test_pmx_exporter.py)
|   |       - __init__.py
|   |
|   +---pmx
|   |       ✓ exporter.py (test_pmx_exporter.py, test_pmx_exporter_hard.py)
|   |       ✓ importer.py (test_pmx_importer_hard.py, multiple test files)
|   |       - __init__.py
|   |
|   +---vmd
|   |       ✓ exporter.py (test_vmd_exporter.py)
|   |       ✓ importer.py (test_vmd_importer.py)
|   |       - __init__.py
|   |
|   \---vpd
|           ✓ exporter.py (test_vpd_exporter.py)
|           ✓ importer.py (test_vpd_importer.py)
|           - __init__.py
|
+---operators
|       ✗ animation.py
|       ✓ camera.py (test_camera_system.py)
|       ✗ display_item.py
|       ✓ fileio.py (test_fileio_operators.py)
|       ✓ lamp.py (test_lamp_system.py)
|       ✓ material.py (test_material_system.py)
|       ✗ misc.py
|       ✓ model.py (test_model_operators.py)
|       ✓ model_edit.py (test_model_edit.py)
|       ✓ model_validation.py (test_model_debug.py)
|       ✓ morph.py (test_morph_system.py)
|       ✓ rigid_body.py (test_rigid_body.py)
|       ✓ sdef.py (test_sdef_system.py)
|       ✗ translations.py
|       ✗ view.py
|       - __init__.py
|
+---panels
|   |   ✓ prop_bone.py (test_bone.py)
|   |   ✓ prop_camera.py (test_camera_system.py)
|   |   ✓ prop_lamp.py (test_lamp_system.py)
|   |   ✓ prop_material.py (test_material_system.py)
|   |   ✗ prop_object.py
|   |   ✗ prop_physics.py
|   |   ✗ shading.py
|   |   - __init__.py
|   |
|   \---sidebar
|           ✓ bone_order.py (test_bone_order.py)
|           ✗ display_panel.py
|           ✗ joints.py
|           ✗ material_sorter.py
|           ✗ meshes_sorter.py
|           ✗ model_debug.py
|           ✗ model_production.py
|           ✗ model_setup.py
|           ✓ morph_tools.py (test_morph_system.py)
|           ✗ rigid_bodies.py
|           ✗ scene_setup.py
|           - __init__.py
|
+---properties
|       ✓ camera.py (test_properties.py)
|       ✓ material.py (test_properties.py)
|       ✓ morph.py (test_properties.py)
|       ✓ pose_bone.py (test_properties.py)
|       ✓ rigid_body.py (test_properties.py)
|       ✓ root.py (test_properties.py)
|       ✓ translations.py (test_properties.py)
|       - __init__.py
|
\---typings
    \---mmd_tools
        \---properties
                - material.pyi
                - morph.pyi
                - pose_bone.pyi
                - root.pyi
                - translations.pyi
```