# Copyright 2025 MMD Tools authors
# This file is part of MMD Tools.

import logging
import os
import shutil
import unittest

import bpy
from bl_ext.blender_org.mmd_tools.core.model import Model

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(os.path.dirname(TESTS_DIR), "samples")


class TestPmxExportVertexMergeBug(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Clean up output from previous tests"""
        output_dir = os.path.join(TESTS_DIR, "output")
        for item in os.listdir(output_dir):
            if item.endswith(".OUTPUT"):
                continue
            item_fp = os.path.join(output_dir, item)
            if os.path.isfile(item_fp):
                os.remove(item_fp)
            elif os.path.isdir(item_fp):
                shutil.rmtree(item_fp)

    def setUp(self):
        """Set up testing environment"""
        logger = logging.getLogger()
        logger.setLevel("ERROR")

    def __enable_mmd_tools(self):
        bpy.ops.wm.read_homefile(use_empty=True)
        pref = getattr(bpy.context, "preferences", None) or bpy.context.user_preferences
        if not pref.addons.get("mmd_tools", None):
            addon_enable = bpy.ops.wm.addon_enable if "addon_enable" in dir(bpy.ops.wm) else bpy.ops.preferences.addon_enable
            addon_enable(module="bl_ext.blender_org.mmd_tools")

    def __list_sample_files(self, file_types):
        ret = []
        for file_type in file_types:
            file_ext = "." + file_type
            for root, dirs, files in os.walk(os.path.join(SAMPLES_DIR, file_type)):
                ret.extend(os.path.join(root, name) for name in files if name.lower().endswith(file_ext))
        return ret

    def __get_model_meshes(self, root_obj):
        """Get all mesh objects belonging to the model"""
        model = Model(root_obj)
        return list(model.meshes())

    def test_merge_vertices_by_distance_standalone(self):
        """Test merge vertices by distance operation causes PMX export failure"""
        input_files = self.__list_sample_files(("pmx",))
        assert len(input_files) >= 1, "No PMX sample files available"

        test_file = input_files[0]

        # Import model
        self.__enable_mmd_tools()
        bpy.ops.mmd_tools.import_model(filepath=test_file, types={"MESH", "ARMATURE", "PHYSICS", "MORPHS", "DISPLAY"}, scale=0.08, clean_model=False, remove_doubles=False, log_level="ERROR")

        # Find the imported model
        root_objects = [obj for obj in bpy.context.scene.objects if obj.mmd_type == "ROOT"]
        assert len(root_objects) > 0, "PMX model should be imported successfully"

        root_obj = root_objects[0]
        meshes = self.__get_model_meshes(root_obj)

        # Find a mesh with enough vertices
        target_mesh = None
        for mesh_obj in meshes:
            if len(mesh_obj.data.vertices) > 100:
                target_mesh = mesh_obj
                break

        assert target_mesh is not None, "No mesh with sufficient vertices found"

        # Perform merge vertices by distance
        bpy.context.view_layer.objects.active = target_mesh
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.object.mode_set(mode="OBJECT")

        # Setup export context
        bpy.ops.object.select_all(action="DESELECT")
        root_obj.select_set(True)
        bpy.context.view_layer.objects.active = root_obj
        bpy.context.view_layer.update()

        # Export should fail - let it crash
        output_pmx = os.path.join(TESTS_DIR, "output", "merge_bug_test.pmx")
        bpy.ops.mmd_tools.export_pmx(filepath=output_pmx, scale=12.5, copy_textures=False, sort_materials=False, sort_vertices="NONE", log_level="ERROR")


if __name__ == "__main__":
    import sys

    sys.argv = [__file__] + (sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    unittest.main(verbosity=1, exit=True)
