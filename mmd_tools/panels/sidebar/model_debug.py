# Copyright 2025 MMD Tools authors
# This file is part of MMD Tools.

import bpy

from ...core.model import FnModel
from . import PT_ProductionPanelBase


class MMDModelDebugPanel(PT_ProductionPanelBase, bpy.types.Panel):
    bl_idname = "OBJECT_PT_mmd_tools_model_debug"
    bl_label = "Model Debug"
    bl_order = 4

    def draw(self, context):
        active_obj = context.active_object

        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Model Validation:", icon="ERROR")

        # Check if we have a valid MMD model selected
        root = FnModel.find_root_object(active_obj)
        col.enabled = root is not None

        # Validation buttons section
        grid = col.grid_flow(row_major=True, columns=2, align=True, even_columns=True)
        grid.operator("mmd_tools.validate_model", text="Check Model", icon="EMPTY_DATA")
        grid.operator("mmd_tools.validate_textures", text="Check Textures", icon="TEXTURE")
        grid.operator("mmd_tools.validate_bones", text="Check Bones", icon="BONE_DATA")
        grid.operator("mmd_tools.validate_morphs", text="Check Morphs", icon="SHAPEKEY_DATA")

        # Results section
        box = layout.box()
        box.label(text="Validation Results:", icon="INFO")

        # Add this section to display the validation results
        if context.scene.mmd_validation_results:
            result_col = box.column(align=True)
            for line in context.scene.mmd_validation_results.split("\n"):
                result_col.label(text=line)
        else:
            col = box.column(align=True)
            col.label(text="Run validation to see results")

        # Fix suggestions section
        col = layout.column(align=True)
        col.label(text="Quick Fixes:", icon="TOOL_SETTINGS")
        col.enabled = root is not None
        grid = col.grid_flow(row_major=True, align=True)

        grid = col.grid_flow(row_major=True, columns=2, align=True, even_columns=True)
        grid.operator("mmd_tools.fix_model_issues", text="Fix Model", icon="OUTLINER_OB_EMPTY")
        grid.operator("mmd_tools.fix_texture_issues", text="Fix Textures", icon="IMAGE_DATA")
        grid.operator("mmd_tools.fix_bone_issues", text="Fix Bones", icon="MODIFIER")
        grid.operator("mmd_tools.fix_morph_issues", text="Fix Morphs", icon="KEY_HLT")
