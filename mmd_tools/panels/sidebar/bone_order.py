# -*- coding: utf-8 -*-
# Copyright 2016 MMD Tools authors
# This file is part of MMD Tools.

import bpy
from ...core.model import FnModel
from . import PT_ProductionPanelBase


class MMDToolsBoneIdMoveUp(bpy.types.Operator):
    bl_idname = "mmd_tools.bone_id_move_up"
    bl_label = "Move Bone ID Up"
    bl_description = "Move active bone up in bone order"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        root = FnModel.find_root_object(context.object)
        armature = FnModel.find_armature_object(root)
        
        if not root or not armature:
            return {'CANCELLED'}
            
        active_bone_index = root.mmd_root.active_bone_index
        if active_bone_index >= len(armature.pose.bones):
            return {'CANCELLED'}
            
        active_bone = armature.pose.bones[active_bone_index]
        active_id = active_bone.mmd_bone.bone_id
        
        # Find bone with smaller bone_id
        prev_bone = None
        prev_id = -1
        
        for bone in armature.pose.bones:
            is_shadow = getattr(bone, 'is_mmd_shadow_bone', False) is True
            if not is_shadow and bone.mmd_bone.bone_id < active_id and bone.mmd_bone.bone_id > prev_id:
                prev_bone = bone
                prev_id = bone.mmd_bone.bone_id
                
        if prev_bone:
            # Swap bone_id
            active_bone.mmd_bone.bone_id, prev_bone.mmd_bone.bone_id = prev_bone.mmd_bone.bone_id, active_bone.mmd_bone.bone_id
            
            # Refresh UI
            for area in context.screen.areas:
                area.tag_redraw()
        
        return {'FINISHED'}


class MMDToolsBoneIdMoveDown(bpy.types.Operator):
    bl_idname = "mmd_tools.bone_id_move_down"
    bl_label = "Move Bone ID Down"
    bl_description = "Move active bone down in bone order"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        root = FnModel.find_root_object(context.object)
        armature = FnModel.find_armature_object(root)
        
        if not root or not armature:
            return {'CANCELLED'}
            
        active_bone_index = root.mmd_root.active_bone_index
        if active_bone_index >= len(armature.pose.bones):
            return {'CANCELLED'}
        
        active_bone = armature.pose.bones[active_bone_index]
        active_id = active_bone.mmd_bone.bone_id
        
        # Find bone with larger bone_id
        next_bone = None
        next_id = float('inf')
        
        for bone in armature.pose.bones:
            is_shadow = getattr(bone, 'is_mmd_shadow_bone', False) is True
            if not is_shadow and bone.mmd_bone.bone_id > active_id and bone.mmd_bone.bone_id < next_id:
                next_bone = bone
                next_id = bone.mmd_bone.bone_id
                
        if next_bone:
            # Swap bone_id
            active_bone.mmd_bone.bone_id, next_bone.mmd_bone.bone_id = next_bone.mmd_bone.bone_id, active_bone.mmd_bone.bone_id
            
            # Refresh UI
            for area in context.screen.areas:
                area.tag_redraw()
        
        return {'FINISHED'}


class MMDToolsSortBonesByBoneId(bpy.types.Operator):
    bl_idname = "mmd_tools.sort_bones_by_bone_id"
    bl_label = "Sort Bones by Bone ID"
    bl_description = "Sort bones by their bone ID"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object
        next_id = 0
        
        # Find max bone_id
        for bone in armature.pose.bones:
            is_shadow = getattr(bone, 'is_mmd_shadow_bone', False) is True
            if not is_shadow and bone.mmd_bone.bone_id >= 0:
                next_id = max(next_id, bone.mmd_bone.bone_id + 1)
                
        # Assign IDs to bones without bone_id
        for bone in armature.pose.bones:
            is_shadow = getattr(bone, 'is_mmd_shadow_bone', False) is True
            if not is_shadow and bone.mmd_bone.bone_id < 0:
                bone.mmd_bone.bone_id = next_id
                next_id += 1
        
        # Refresh UI
        for area in context.screen.areas:
            area.tag_redraw()
                
        return {'FINISHED'}


class MMDToolsRealignBoneIds(bpy.types.Operator):
    bl_idname = "mmd_tools.realign_bone_ids"
    bl_label = "Realign Bone IDs"
    bl_description = "Realign bone IDs to be sequential without gaps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        root = FnModel.find_root_object(context.object)
        armature = FnModel.find_armature_object(root)
        
        if not root or not armature:
            return {'CANCELLED'}
        
        # Get all bones with valid bone_id, sorted by bone_id
        valid_bones = []
        for bone in armature.pose.bones:
            is_shadow = getattr(bone, 'is_mmd_shadow_bone', False) is True
            if not is_shadow and bone.mmd_bone.bone_id >= 0:
                valid_bones.append(bone)
        
        # Sort by current bone_id
        valid_bones.sort(key=lambda b: b.mmd_bone.bone_id)
        
        # Reassign sequential bone_ids
        for i, bone in enumerate(valid_bones):
            bone.mmd_bone.bone_id = i
        
        # Refresh UI
        for area in context.screen.areas:
            area.tag_redraw()
        
        return {'FINISHED'}


class MMD_TOOLS_UL_ModelBones(bpy.types.UIList):
    # Static data for bone relationships
    _IK_MAP = {}
    _IK_BONES = {}
    _bone_order_map = {}

    @classmethod
    def update_bone_tables(cls, armature):
        """Update bone relationship tables"""
        cls._IK_MAP.clear()
        cls._IK_BONES.clear()
        cls._bone_order_map.clear()

        # Process IK relationships
        valid_bone_count = 0
        
        for bone in armature.pose.bones:
            is_shadow = getattr(bone, 'is_mmd_shadow_bone', False) is True
            if is_shadow:
                continue
                
            valid_bone_count += 1
                
            # Process IK constraints
            for constraint in bone.constraints:
                if constraint.type == "IK" and constraint.subtarget in armature.pose.bones:
                    if not constraint.use_tail:
                        cls._IK_MAP.setdefault(hash(bone), []).append(constraint.subtarget)
                        cls._IK_BONES[constraint.subtarget] = hash(bone)
                        bone_chain = bone.parent_recursive
                    else:
                        cls._IK_BONES[constraint.subtarget] = bone.name
                        bone_chain = [bone] + bone.parent_recursive
                        
                    # Add all bones in IK chain
                    for linked_bone in bone_chain[:constraint.chain_count]:
                        cls._IK_MAP.setdefault(hash(linked_bone), []).append(constraint.subtarget)
        
        # Process special IK connections
        for subtarget, value in tuple(cls._IK_BONES.items()):
            if isinstance(value, str):
                target_bone = cls.__get_ik_target_bone(armature.pose.bones[value])
                if target_bone:
                    cls._IK_BONES[subtarget] = hash(target_bone)
                    cls._IK_MAP.setdefault(hash(target_bone), []).append(subtarget)
                else:
                    del cls._IK_BONES[subtarget]
                    
        # Update bone sorting
        cls.update_sorted_bones(armature)
        
        return valid_bone_count

    @classmethod
    def update_sorted_bones(cls, armature):
        """Update bone order mapping"""
        cls._bone_order_map.clear()
        
        # Create index to bone_id mapping
        bone_id_list = []
        for i, bone in enumerate(armature.pose.bones):
            is_shadow = getattr(bone, 'is_mmd_shadow_bone', False) is True
            if not is_shadow:
                bone_id = bone.mmd_bone.bone_id if hasattr(bone.mmd_bone, 'bone_id') else -1
                bone_id_list.append((i, bone_id))
        
        # Sort by bone_id
        bone_id_list.sort(key=lambda x: x[1] if x[1] >= 0 else float('inf'))
        
        # Create order mapping
        for new_idx, (orig_idx, _) in enumerate(bone_id_list):
            cls._bone_order_map[orig_idx] = new_idx

    @staticmethod
    def __get_ik_target_bone(target_bone):
        """Find the IK target bone from a parent bone"""
        r = None
        min_length = None
        for child in target_bone.children:
            is_shadow = getattr(child, 'is_mmd_shadow_bone', False) is True
            if is_shadow:
                continue
            if child.bone.use_connect:
                return child
            length = (child.head - target_bone.tail).length
            if min_length is None or length < min_length:
                min_length = length
                r = child
        return r

    def filter_items(self, context, data, propname):
        """Filter and sort items"""
        bones = getattr(data, propname)
        bone_count = len(bones)
        
        # Filter out shadow bones
        filtered_flags = []
        for bone in bones:
            is_shadow = getattr(bone, 'is_mmd_shadow_bone', False) is True
            if is_shadow:
                filtered_flags.append(0)  # Filter out shadow bones
            else:
                filtered_flags.append(self.bitflag_filter_item)  # Show non-shadow bones
        
        # Use defined sort order
        if not self._bone_order_map:
            # If no sort mapping yet, update once
            self.update_sorted_bones(data)
            
        ordered_indices = []
        for i in range(bone_count):
            if filtered_flags[i]:  # Only sort displayed bones
                ordered_indices.append(self._bone_order_map.get(i, i))
            else:
                ordered_indices.append(i)  # Keep filtered items in original position
        
        return filtered_flags, ordered_indices

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {"DEFAULT"}:
            self._draw_bone_item(layout, item)
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)

    @classmethod
    def _draw_bone_item(cls, layout, bone):
        """Draw a single bone item in the UI list"""
        is_shadow = False
        if bone:
            is_shadow = getattr(bone, 'is_mmd_shadow_bone', False) is True
            
        if not bone or is_shadow:
            layout.active = False
            layout.label(text=bone.name if bone else "", translate=False, icon="GROUP_BONE" if bone else "MESH_DATA")
            return

        bone_id = bone.mmd_bone.bone_id if bone.mmd_bone.bone_id >= 0 else -1
        count = len(bone.id_data.pose.bones)
        bone_transform_rank = bone_id + bone.mmd_bone.transform_order * count

        row = layout.split(factor=0.45, align=False)
        r0 = row.row()
        r0.label(text=bone.name, translate=False, icon="POSE_HLT" if bone.name in cls._IK_BONES else "BONE_DATA")
        r = r0.row()
        r.alignment = "RIGHT"
        r.label(text=str(bone_id))

        row_sub = row.split(factor=0.67, align=False)

        # Display bone relationships
        r = row_sub.row()

        # Display parent bone
        bone_parent = bone.parent
        if bone_parent:
            parent_bone_id = bone_parent.mmd_bone.bone_id if bone_parent.mmd_bone.bone_id >= 0 else -1
            parent_icon = "ERROR"
            if parent_bone_id >= 0:
                if bone_transform_rank >= (parent_bone_id + bone_parent.mmd_bone.transform_order * count):
                    parent_icon = "INFO" if bone_id < parent_bone_id else "FILE_PARENT"
            r.label(text=str(parent_bone_id), icon=parent_icon)
        else:
            r.label()

        # Display additional transforms
        r = r.row()
        mmd_bone = bone.mmd_bone
        if mmd_bone.has_additional_rotation or mmd_bone.has_additional_location:
            append_bone_name = mmd_bone.additional_transform_bone
            if append_bone_name in bone.id_data.pose.bones:
                append_bone = bone.id_data.pose.bones[append_bone_name]
                append_bone_id = append_bone.mmd_bone.bone_id if append_bone.mmd_bone.bone_id >= 0 else -1
                
                icon = "ERROR"
                if append_bone_id >= 0 and bone_transform_rank >= (append_bone_id + append_bone.mmd_bone.transform_order * count):
                    if mmd_bone.has_additional_rotation and mmd_bone.has_additional_location:
                        icon = "IPO_QUAD"
                    elif mmd_bone.has_additional_rotation:
                        icon = "IPO_EXPO"
                    else:
                        icon = "IPO_LINEAR"
                        
                if append_bone_name:
                    r.label(text=str(append_bone_id), icon=icon)

        # Display IK connections with index-based sorting (like the old version)
        ik_bones_data = []
        for ik_bone_name in cls._IK_MAP.get(hash(bone), []):
            ik_bone = bone.id_data.pose.bones[ik_bone_name]
            ik_bone_id = ik_bone.mmd_bone.bone_id if ik_bone.mmd_bone.bone_id >= 0 else -1
            is_ik_chain = hash(bone) != cls._IK_BONES.get(ik_bone_name)

            icon = "LINKED" if is_ik_chain else "HOOK"
            if ik_bone_id < 0:
                icon = "ERROR"
            elif is_ik_chain and bone_transform_rank > (ik_bone_id + ik_bone.mmd_bone.transform_order * count):
                icon = "ERROR"

            # Store for sorting
            ik_bones_data.append((ik_bone_id, ik_bone, icon))

        # Sort by bone_id (similar to the old version's vertex_group index sorting)
        for bone_id, ik_bone, icon in sorted(ik_bones_data, key=lambda x: x[0] if x[0] >= 0 else float('inf')):
            r.prop(ik_bone, "mmd_ik_toggle", text=str(bone_id), toggle=True, icon=icon)

        # Display transform order and post-dynamics transform
        row = row_sub.row(align=True)
        # Fix: Use a specific icon name instead of None
        if mmd_bone.transform_after_dynamics:
            row.prop(mmd_bone, "transform_after_dynamics", text="", toggle=True, icon="PHYSICS")
        else:
            row.prop(mmd_bone, "transform_after_dynamics", text="", toggle=True, icon="BLANK1")
        row.prop(mmd_bone, "transform_order", text="", slider=bool(mmd_bone.transform_order))


class MMDBoneOrderMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_mmd_tools_bone_order_menu"
    bl_label = "Bone Order Menu"

    def draw(self, _context):
        layout = self.layout
        layout.operator("mmd_tools.sort_bones_by_bone_id", text="Sort by Bone ID", icon="SORTALPHA")


class MMDBoneOrder(PT_ProductionPanelBase, bpy.types.Panel):
    bl_idname = "OBJECT_PT_mmd_tools_bone_order"
    bl_label = "Bone Order"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 5

    def draw(self, context):
        layout = self.layout
        active_obj = context.active_object
        root = FnModel.find_root_object(active_obj)
        if root is None:
            layout.label(text="Select a MMD Model")
            return

        armature = FnModel.find_armature_object(root)
        if armature is None:
            layout.label(text="The armature object of active MMD model can't be found", icon="ERROR")
            return

        # Update bone tables
        valid_bone_count = MMD_TOOLS_UL_ModelBones.update_bone_tables(armature)

        # UI
        col = layout.column(align=True)
        row = col.row()

        # Bone list sorted by bone_id
        row.template_list("MMD_TOOLS_UL_ModelBones", "", armature.pose, "bones", root.mmd_root, "active_bone_index")

        # Bone order controls
        tb = row.column()
        tb1 = tb.column(align=True)
        tb1.menu("OBJECT_MT_mmd_tools_bone_order_menu", text="", icon="DOWNARROW_HLT")
        tb.separator()
        tb1 = tb.column(align=True)
        tb1.operator("mmd_tools.bone_id_move_up", text="", icon="TRIA_UP")
        tb1.operator("mmd_tools.bone_id_move_down", text="", icon="TRIA_DOWN")

        # Display total bone count with realign button
        row = col.row(align=True)
        row.label(text=f"Total Bones: {valid_bone_count}")
        row.operator("mmd_tools.realign_bone_ids", text="Align IDs", icon="LINENUMBERS_ON")