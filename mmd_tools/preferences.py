# Copyright 2022 MMD Tools authors
# This file is part of MMD Tools.

import os

import bpy


def get_preset_items_for_operator(operator_bl_idname):
    """Get preset items for EnumProperty"""
    items = [("", "None", "Use built-in defaults")]
    try:
        from .operators import fileio

        presets = fileio.get_available_presets(operator_bl_idname)
        for preset in presets:
            items.append((preset, preset, f"Use preset: {preset}"))
    except Exception:
        pass
    return items


def get_pmx_import_preset_items(self, context):
    return get_preset_items_for_operator("mmd_tools.import_model")


def get_vmd_import_preset_items(self, context):
    return get_preset_items_for_operator("mmd_tools.import_vmd")


def get_vpd_import_preset_items(self, context):
    return get_preset_items_for_operator("mmd_tools.import_vpd")


def get_pmx_export_preset_items(self, context):
    return get_preset_items_for_operator("mmd_tools.export_pmx")


def get_vmd_export_preset_items(self, context):
    return get_preset_items_for_operator("mmd_tools.export_vmd")


def get_vpd_export_preset_items(self, context):
    return get_preset_items_for_operator("mmd_tools.export_vpd")


class MMDToolsAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    enable_mmd_model_production_features: bpy.props.BoolProperty(
        name="Enable MMD Model Production Features",
        default=True,
    )
    shared_toon_folder: bpy.props.StringProperty(
        name="Shared Toon Texture Folder",
        description=('Directory path to toon textures. This is normally the "Data" directory within of your MikuMikuDance directory'),
        subtype="DIR_PATH",
        default=os.path.join(os.path.dirname(__file__), "externals", "MikuMikuDance"),
    )
    base_texture_folder: bpy.props.StringProperty(
        name="Base Texture Folder",
        description="Path for textures shared between models",
        subtype="DIR_PATH",
    )
    dictionary_folder: bpy.props.StringProperty(
        name="Dictionary Folder",
        description="Path for searching csv dictionaries",
        subtype="DIR_PATH",
        default=os.path.dirname(__file__),
    )

    # Preset selection properties
    default_pmx_import_preset: bpy.props.EnumProperty(
        name="Default PMX Import Preset",
        description="Default preset to use for PMX import operations",
        items=get_pmx_import_preset_items,
        default=0,
    )
    default_vmd_import_preset: bpy.props.EnumProperty(
        name="Default VMD Import Preset",
        description="Default preset to use for VMD import operations",
        items=get_vmd_import_preset_items,
        default=0,
    )
    default_vpd_import_preset: bpy.props.EnumProperty(
        name="Default VPD Import Preset",
        description="Default preset to use for VPD import operations",
        items=get_vpd_import_preset_items,
        default=0,
    )
    default_pmx_export_preset: bpy.props.EnumProperty(
        name="Default PMX Export Preset",
        description="Default preset to use for PMX export operations",
        items=get_pmx_export_preset_items,
        default=0,
    )
    default_vmd_export_preset: bpy.props.EnumProperty(
        name="Default VMD Export Preset",
        description="Default preset to use for VMD export operations",
        items=get_vmd_export_preset_items,
        default=0,
    )
    default_vpd_export_preset: bpy.props.EnumProperty(
        name="Default VPD Export Preset",
        description="Default preset to use for VPD export operations",
        items=get_vpd_export_preset_items,
        default=0,
    )

    def draw(self, _context):
        layout: bpy.types.UILayout = self.layout  # pylint: disable=no-member
        layout.prop(self, "enable_mmd_model_production_features")
        layout.prop(self, "shared_toon_folder")
        layout.prop(self, "base_texture_folder")
        layout.prop(self, "dictionary_folder")

        layout.separator()
        layout.label(text="Default Presets:")
        layout.prop(self, "default_pmx_import_preset", text="PMX Import")
        layout.prop(self, "default_pmx_export_preset", text="PMX Export")
        layout.prop(self, "default_vmd_import_preset", text="VMD Import")
        layout.prop(self, "default_vmd_export_preset", text="VMD Export")
        layout.prop(self, "default_vpd_import_preset", text="VPD Import")
        layout.prop(self, "default_vpd_export_preset", text="VPD Export")
