# -*- coding: utf-8 -*-
# Copyright 2022 MMD Tools authors
# This file is part of MMD Tools.

import os
import sys
import subprocess
import importlib
import bpy
from bpy.props import BoolProperty, StringProperty


# ===== Dependency Management System =====

# Dictionary of optional dependencies
OPTIONAL_DEPENDENCIES = {
    "opencc": {"display_name": "OpenCC", "description": "For non-Japanese bone/morph name conversion", "package_name": "opencc", "module_name": "opencc", "icon": "WORLD"},
    # Additional dependencies can be added here in the future
}


# Check if a dependency is installed
def is_dependency_installed(module_name):
    try:
        # Force a fresh import attempt rather than using cached result
        if module_name in sys.modules:
            del sys.modules[module_name]

        # Try to import the module
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


# Base class for dependency installation operators
class MMDT_OT_InstallDependency(bpy.types.Operator):
    """Install a dependency for MMD Tools"""

    bl_idname = "mmdt.install_dependency"
    bl_label = "Install Dependency"
    bl_description = "Install a dependency for MMD Tools"
    bl_options = {"REGISTER", "INTERNAL"}

    dependency_id: StringProperty(name="Dependency ID", description="Identifier for the dependency to install", default="")

    def execute(self, context):
        if not self.dependency_id or self.dependency_id not in OPTIONAL_DEPENDENCIES:
            self.report({"ERROR"}, "Invalid dependency specified")
            return {"CANCELLED"}

        dependency = OPTIONAL_DEPENDENCIES[self.dependency_id]

        try:
            # Get Python interpreter path (compatible with Blender 4.4+)
            python_exe = sys.executable

            # Use subprocess to install dependency
            subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.check_call([python_exe, "-m", "pip", "install", dependency["package_name"]])

            # Force reload the importlib.metadata cache to immediately detect the newly installed package
            importlib.invalidate_caches()

            # Force UI redraw
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

            self.report({"INFO"}, f"{dependency['display_name']} installed successfully. Please restart Blender.")
            return {"FINISHED"}
        except subprocess.CalledProcessError as e:
            self.report({"ERROR"}, f"Failed to install {dependency['display_name']}: {str(e)}")
            return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"Unexpected error: {str(e)}")
            return {"CANCELLED"}


# Base class for dependency uninstallation operators
class MMDT_OT_UninstallDependency(bpy.types.Operator):
    """Uninstall a dependency from MMD Tools"""

    bl_idname = "mmdt.uninstall_dependency"
    bl_label = "Uninstall Dependency"
    bl_description = "Uninstall a dependency from MMD Tools"
    bl_options = {"REGISTER", "INTERNAL"}

    dependency_id: StringProperty(name="Dependency ID", description="Identifier for the dependency to uninstall", default="")

    def execute(self, context):
        if not self.dependency_id or self.dependency_id not in OPTIONAL_DEPENDENCIES:
            self.report({"ERROR"}, "Invalid dependency specified")
            return {"CANCELLED"}

        dependency = OPTIONAL_DEPENDENCIES[self.dependency_id]

        try:
            # Get Python interpreter path (compatible with Blender 4.4+)
            python_exe = sys.executable

            # Use subprocess to uninstall dependency
            subprocess.check_call([python_exe, "-m", "pip", "uninstall", "-y", dependency["package_name"]])

            # Force reload the importlib.metadata cache to immediately detect the removed package
            importlib.invalidate_caches()

            # Force UI redraw
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

            self.report({"INFO"}, f"{dependency['display_name']} uninstalled successfully. Please restart Blender.")
            return {"FINISHED"}
        except subprocess.CalledProcessError as e:
            self.report({"ERROR"}, f"Failed to uninstall {dependency['display_name']}: {str(e)}")
            return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"Unexpected error: {str(e)}")
            return {"CANCELLED"}


class MMDToolsAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    enable_mmd_model_production_features: BoolProperty(
        name="Enable MMD Model Production Features",
        default=True,
    )
    shared_toon_folder: StringProperty(
        name="Shared Toon Texture Folder",
        description=('Directory path to toon textures. This is normally the "Data" directory within of your MikuMikuDance directory'),
        subtype="DIR_PATH",
        default=os.path.join(os.path.dirname(__file__), "externals", "MikuMikuDance"),
    )
    base_texture_folder: StringProperty(
        name="Base Texture Folder",
        description="Path for textures shared between models",
        subtype="DIR_PATH",
    )
    dictionary_folder: StringProperty(
        name="Dictionary Folder",
        description="Path for searching csv dictionaries",
        subtype="DIR_PATH",
        default=os.path.dirname(__file__),
    )

    def draw(self, _context):
        layout: bpy.types.UILayout = self.layout  # pylint: disable=no-member
        layout.prop(self, "enable_mmd_model_production_features")
        layout.separator()
        layout.prop(self, "shared_toon_folder")
        layout.prop(self, "base_texture_folder")
        layout.prop(self, "dictionary_folder")

        # Optional Dependencies Section
        layout.separator()
        layout.label(text="Optional Dependencies:")

        # Display each dependency status
        for dep_id, dependency in OPTIONAL_DEPENDENCIES.items():
            row = layout.row()
            status_text = f"{dependency['display_name']}: {dependency['description']}"
            row.label(text=status_text, icon=dependency["icon"])

            # Install/Uninstall button
            sub_row = row.row()
            sub_row.alignment = "RIGHT"

            if is_dependency_installed(dependency["module_name"]):
                op = sub_row.operator(MMDT_OT_UninstallDependency.bl_idname, text="Uninstall", icon="TRASH")
                op.dependency_id = dep_id
            else:
                op = sub_row.operator(MMDT_OT_InstallDependency.bl_idname, text="Install", icon="IMPORT")
                op.dependency_id = dep_id
