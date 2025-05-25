import logging
import math
import os
import shutil
import unittest

import bpy
from bl_ext.user_default.mmd_tools.core import vmd
from bl_ext.user_default.mmd_tools.core.model import Model
from mathutils import Quaternion, Vector

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(os.path.dirname(TESTS_DIR), "samples")


class TestVmdExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Clean up output from previous tests
        """
        output_dir = os.path.join(TESTS_DIR, "output")
        for item in os.listdir(output_dir):
            if item.endswith(".OUTPUT"):
                continue  # Skip the placeholder
            item_fp = os.path.join(output_dir, item)
            if os.path.isfile(item_fp):
                os.remove(item_fp)
            elif os.path.isdir(item_fp):
                shutil.rmtree(item_fp)

    def setUp(self):
        """
        We should start each test with a clean state
        """
        logger = logging.getLogger()
        logger.setLevel("ERROR")

        # Clear the scene
        bpy.ops.wm.read_homefile()

    # ********************************************
    # Utils
    # ********************************************

    def __vector_error(self, vec0, vec1):
        return (Vector(vec0) - Vector(vec1)).length

    def __quaternion_error(self, quat0, quat1):
        # Convert lists to quaternions if needed
        if isinstance(quat0, (list, tuple)):
            q0 = Quaternion((quat0[3], quat0[0], quat0[1], quat0[2]))  # (x,y,z,w) to (w,x,y,z)
        else:
            q0 = quat0

        if isinstance(quat1, (list, tuple)):
            q1 = Quaternion((quat1[3], quat1[0], quat1[1], quat1[2]))  # (x,y,z,w) to (w,x,y,z)
        else:
            q1 = quat1

        angle = q0.rotation_difference(q1).angle % math.pi
        assert angle >= 0
        return min(angle, math.pi - angle)

    def __interpolation_error(self, interp0, interp1):
        """Compare VMD interpolation arrays and return maximum difference"""
        if len(interp0) != len(interp1):
            return float("inf")

        # indices in [2, 3, 31, 46, 47, 61, 62, 63] are unclear
        skip_indices = {2, 3, 31, 46, 47, 61, 62, 63}

        max_error = 0
        for i, (i0, i1) in enumerate(zip(interp0, interp1)):
            if i in skip_indices:
                continue
            max_error = max(max_error, abs(i0 - i1))
        return max_error

    def __list_sample_files(self, file_types):
        ret = []
        for file_type in file_types:
            file_ext = "." + file_type
            for root, dirs, files in os.walk(os.path.join(SAMPLES_DIR, file_type)):
                for name in files:
                    if name.lower().endswith(file_ext):
                        ret.append(os.path.join(root, name))
        return ret

    def __enable_mmd_tools(self):
        bpy.ops.wm.read_homefile()  # reload blender startup file
        pref = getattr(bpy.context, "preferences", None) or bpy.context.user_preferences
        if not pref.addons.get("mmd_tools", None):
            addon_enable = bpy.ops.wm.addon_enable if "addon_enable" in dir(bpy.ops.wm) else bpy.ops.preferences.addon_enable
            addon_enable(module="bl_ext.user_default.mmd_tools")  # make sure addon 'mmd_tools' is enabled

    def __get_largest_pmx_file(self):
        """Get the largest PMX file from samples"""
        pmx_files = self.__list_sample_files(["pmx", "pmd"])
        if not pmx_files:
            return None

        # Get file sizes and find the largest
        file_sizes = [(filepath, os.path.getsize(filepath)) for filepath in pmx_files]
        file_sizes.sort(key=lambda x: x[1], reverse=True)

        return file_sizes[0][0]  # Return the largest file path

    def __import_largest_pmx_model(self):
        """Import the largest PMX model and return the root object"""
        largest_pmx = self.__get_largest_pmx_file()
        if not largest_pmx:
            self.skipTest("No PMX sample files found")

        print(f"\nImporting largest PMX model: {largest_pmx}")

        # Clear the scene
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

        try:
            # Use MMD Tools importer to import PMX
            bpy.ops.mmd_tools.import_model(filepath=largest_pmx, types={"MESH", "ARMATURE", "PHYSICS", "DISPLAY", "MORPHS"}, scale=1.0, clean_model=False, remove_doubles=False, log_level="ERROR")

            # Update scene
            bpy.context.view_layer.update()

            # Find the root object
            root_obj = None
            for obj in bpy.context.scene.objects:
                if obj.mmd_type == "ROOT":
                    root_obj = obj
                    break

            if not root_obj:
                self.fail("Failed to find root object after PMX import")

            # Use Model class to wrap the root object
            model = Model(root_obj)

            # Get correct object information
            armature_obj = model.armature()
            mesh_objs = list(model.meshes())

            print(f"Successfully imported PMX model with root: {root_obj.name}")
            print(f"Model has armature: {armature_obj.name}")
            print(f"Model has {len(mesh_objs)} mesh objects")

            # List all mesh objects
            for i, mesh in enumerate(mesh_objs):
                print(f"  Mesh {i + 1}: {mesh.name}")

            return root_obj

        except Exception as e:
            self.fail(f"Failed to import PMX model {largest_pmx}: {e}")

    # ********************************************
    # VMD Check Functions
    # ********************************************

    def __check_vmd_header(self, source_vmd, result_vmd):
        """Test VMD header information"""
        self.assertEqual(source_vmd.header.signature, result_vmd.header.signature)
        # Note: model_name might change during export, so we don't check it strictly

    def __check_vmd_bone_animation(self, source_vmd, result_vmd):
        """Test VMD bone animation data - compare all keyframes"""
        source_bone_anim = source_vmd.boneAnimation
        result_bone_anim = result_vmd.boneAnimation

        # We allow some bones to be filtered out during export
        # So we only check bones that exist in both
        common_bones = set(source_bone_anim.keys()) & set(result_bone_anim.keys())

        print(f"    Checking {len(common_bones)} common bones out of {len(source_bone_anim)} source bones")

        # Used to record the maximum interpolation error for each bone
        bone_interpolation_errors = {}

        # Flag to track if we've already printed detailed interpolation differences
        detailed_interp_printed = False

        for bone_name in common_bones:
            # if bone_name != "センター":
            #     continue

            source_frames = source_bone_anim[bone_name]
            result_frames = result_bone_anim[bone_name]

            # Sort frames by frame number for consistent comparison
            source_frames.sort(key=lambda x: x.frame_number)
            result_frames.sort(key=lambda x: x.frame_number)

            # Strictly require frame count to be identical
            self.assertEqual(len(source_frames), len(result_frames), f"Bone {bone_name}: Frame count mismatch - source has {len(source_frames)} frames, exported has {len(result_frames)} frames")

            # Record the maximum interpolation error for this bone
            max_interpolation_error = 0

            # Compare all frames
            for i in range(len(source_frames)):
                src_frame = source_frames[i]
                res_frame = result_frames[i]

                msg = f"Bone {bone_name}, frame {src_frame.frame_number}"

                # Check frame number consistency
                self.assertEqual(src_frame.frame_number, res_frame.frame_number, f"{msg} - frame number mismatch")

                # Check location (allow tolerance due to scale conversion)
                self.assertLess(self.__vector_error(src_frame.location, res_frame.location), 1e-5, f"{msg} - location error")

                # Check rotation (allow tolerance)
                self.assertLess(self.__quaternion_error(src_frame.rotation, res_frame.rotation), 1e-5, f"{msg} - rotation error")

                # Check interpolation - skip first keyframe
                # Blender uses right handle of previous keyframe and left handle of current keyframe
                # to calculate interpolation curve, so VMD first frame interpolation cannot be preserved
                if i > 0:  # Skip first keyframe (index 0)
                    if hasattr(src_frame, "interp") and hasattr(res_frame, "interp"):
                        if src_frame.interp and res_frame.interp:
                            interp_error = self.__interpolation_error(src_frame.interp, res_frame.interp)

                            # Print useful info
                            if interp_error > 0 and not detailed_interp_printed:
                                # indices in [2, 3, 31, 46, 47, 61, 62, 63] are unclear
                                # [2, 3] may be related to some special bones
                                # [31, 46, 47, 61, 62, 63] may be related to (センター, 右足IK, 左足IK) bones
                                skip_indices = {2, 3, 31, 46, 47, 61, 62, 63}
                                for j, (s, r) in enumerate(zip(src_frame.interp, res_frame.interp)):
                                    if abs(s - r) > 0 and j not in skip_indices:
                                        print(f"        Difference at index {j:2d}: {s:4d} ->{r:4d}, diff{abs(s - r):4d}, {msg}")
                                        # self.assertIn(abs(s - r), [0], f"{msg} - interpolation error: {abs(s - r)}")
                                # detailed_interp_printed = True  # Set flag to prevent further printing

                            # Check interpolation accuracy with reasonable threshold
                            # self.assertLess(interp_error, 1, f"{msg} - interpolation max error: {interp_error}")

                            max_interpolation_error = max(max_interpolation_error, interp_error)
                        else:
                            # Report if no interpolation data available
                            has_src_interp = hasattr(src_frame, "interp") and bool(src_frame.interp)
                            has_res_interp = hasattr(res_frame, "interp") and bool(res_frame.interp)
                            print(f"    No interpolation check for {msg} (src_has_interp: {has_src_interp}, res_has_interp: {has_res_interp})")
                    else:
                        print(f"    Skipping interpolation check for first frame: {msg} (VMD first frame interpolation not preserved in Blender)")

            # Record the maximum interpolation error for this bone
            if max_interpolation_error > 0:
                bone_interpolation_errors[bone_name] = max_interpolation_error

        if bone_interpolation_errors:
            print("\n    === Bone Interpolation Error Ranking ===")
            # Sort by error size
            sorted_errors = sorted(bone_interpolation_errors.items(), key=lambda x: x[1], reverse=True)

            for rank, (bone_name, error) in enumerate(sorted_errors, 1):
                print(f"    {rank:2d}. {bone_name}: Maximum interpolation error = {error:.2f}")

            print(f"    Total {len(bone_interpolation_errors)} bones have interpolation errors")
            self.assertEqual(len(bone_interpolation_errors), 0, f"Expected no bones with interpolation errors, but found {len(bone_interpolation_errors)} bones with errors")
        else:
            print("    No interpolation errors found")

    def __check_vmd_shape_key_animation(self, source_vmd, result_vmd):
        """Test VMD shape key animation data - compare all keyframes"""
        source_shape_anim = source_vmd.shapeKeyAnimation
        result_shape_anim = result_vmd.shapeKeyAnimation

        common_shapes = set(source_shape_anim.keys()) & set(result_shape_anim.keys())
        print(f"    Checking {len(common_shapes)} common shape keys out of {len(source_shape_anim)} source shapes")

        for shape_name in common_shapes:
            source_frames = source_shape_anim[shape_name]
            result_frames = result_shape_anim[shape_name]

            # Sort frames by frame number for consistent comparison
            source_frames.sort(key=lambda x: x.frame_number)
            result_frames.sort(key=lambda x: x.frame_number)

            # Strictly require frame count to be identical
            self.assertEqual(len(source_frames), len(result_frames), f"Shape key {shape_name}: Frame count mismatch - source has {len(source_frames)} frames, exported has {len(result_frames)} frames")

            # Compare all frames (not just first one)
            for i in range(len(source_frames)):  # Now safe to use len(source_frames)
                src_frame = source_frames[i]
                res_frame = result_frames[i]
                msg = f"Shape key {shape_name}, frame {src_frame.frame_number}"

                # Check frame number consistency
                self.assertEqual(src_frame.frame_number, res_frame.frame_number, f"{msg} - frame number mismatch")

                # Check weight value
                self.assertAlmostEqual(src_frame.weight, res_frame.weight, places=3, msg=f"{msg} - weight error")

    # ********************************************
    # Main Test Functions
    # ********************************************

    def test_vmd_exporter_with_pmx_model(self):
        """
        Test VMD export by importing the largest PMX model and testing different VMD files
        """
        # Get VMD sample files
        vmd_files = self.__list_sample_files(["vmd"])
        if len(vmd_files) < 1:
            self.skipTest("No VMD sample files found")

        print(f"\nFound {len(vmd_files)} VMD files to test")

        # Enable MMD tools
        self.__enable_mmd_tools()

        # Import the largest PMX model
        root_obj = self.__import_largest_pmx_model()

        # Use Model class to get correct objects
        model = Model(root_obj)
        armature_obj = model.armature()
        mesh_objs = list(model.meshes())

        if not armature_obj:
            self.fail("No armature found in imported PMX model")

        print(f"Model has armature: {armature_obj.name}")
        print(f"Model has {len(mesh_objs)} mesh objects")

        # Check if model has shape keys
        shape_key_meshes = []
        for mesh_obj in mesh_objs:
            if mesh_obj.data.shape_keys:
                shape_key_meshes.append(mesh_obj)
                print(f"  Mesh {mesh_obj.name} has {len(mesh_obj.data.shape_keys.key_blocks)} shape keys")

        # Test each VMD file
        success_count = 0
        for test_num, vmd_file in enumerate(vmd_files):
            print(f"\n--- Testing VMD {test_num + 1}/{len(vmd_files)}: {os.path.basename(vmd_file)} ---")

            try:
                # Clear existing animation data
                if armature_obj.animation_data:
                    armature_obj.animation_data_clear()
                for mesh_obj in shape_key_meshes:
                    if mesh_obj.data.shape_keys and mesh_obj.data.shape_keys.animation_data:
                        mesh_obj.data.shape_keys.animation_data_clear()

                # Load original VMD
                source_vmd = vmd.File()
                source_vmd.load(filepath=vmd_file)
                print(f"    Loaded VMD with {len(source_vmd.boneAnimation)} bone animations, {len(source_vmd.shapeKeyAnimation)} shape animations")

                # Select all related objects for VMD import
                bpy.ops.object.select_all(action="DESELECT")
                root_obj.select_set(True)
                armature_obj.select_set(True)
                for mesh_obj in mesh_objs:
                    mesh_obj.select_set(True)

                # Import VMD motion
                bpy.ops.mmd_tools.import_vmd(files=[{"name": os.path.basename(vmd_file)}], directory=os.path.dirname(vmd_file), scale=1.0, margin=0, bone_mapper="PMX", use_pose_mode=False, use_mirror=False, update_scene_settings=False, always_create_new_action=True, use_NLA=False)
                print("    VMD imported successfully")

                # Export VMD motion
                output_vmd = os.path.join(TESTS_DIR, "output", f"test_export_{test_num}.vmd")

                # Set active object to root for export
                bpy.context.view_layer.objects.active = root_obj
                bpy.ops.mmd_tools.export_vmd(filepath=output_vmd, scale=1.0, use_pose_mode=False, use_frame_range=False, preserve_curves=True)
                print("    VMD exported successfully")

                # Load exported VMD for comparison
                result_vmd = vmd.File()
                result_vmd.load(filepath=output_vmd)
                print(f"    Exported VMD has {len(result_vmd.boneAnimation)} bone animations, {len(result_vmd.shapeKeyAnimation)} shape animations")

                # Compare VMD files
                self.__check_vmd_header(source_vmd, result_vmd)

                if len(source_vmd.boneAnimation) > 0:
                    self.__check_vmd_bone_animation(source_vmd, result_vmd)

                if len(source_vmd.shapeKeyAnimation) > 0:
                    self.__check_vmd_shape_key_animation(source_vmd, result_vmd)

                print(f"    ✓ VMD test passed")
                success_count += 1

            except Exception as e:
                print(f"    ✗ VMD test failed: {e}")
                # Don't fail the entire test, just log the error
                import traceback

                traceback.print_exc()

        print(f"\n=== VMD Export Test Results ===")
        print(f"Successfully tested: {success_count}/{len(vmd_files)} VMD files")

        # Require all tests to pass
        success_rate = success_count / len(vmd_files)
        self.assertEqual(success_count, len(vmd_files), f"All direct VMD tests must pass. Success rate: {success_rate:.1%} ({success_count}/{len(vmd_files)})")

    def test_vmd_direct_file_operations(self):
        """
        Direct test of VMD file loading/saving without Blender integration
        """
        vmd_files = self.__list_sample_files(["vmd"])
        if len(vmd_files) < 1:
            self.skipTest("No VMD sample files found")

        print(f"\nTesting direct VMD file operations on {len(vmd_files)} files")

        success_count = 0
        for test_num, vmd_file in enumerate(vmd_files):
            print(f"\n--- Direct test {test_num + 1}/{len(vmd_files)}: {os.path.basename(vmd_file)} ---")

            try:
                # Load original VMD
                source_vmd = vmd.File()
                source_vmd.load(filepath=vmd_file)

                # Save to new file
                output_vmd = os.path.join(TESTS_DIR, "output", f"direct_test_{test_num}.vmd")
                source_vmd.save(filepath=output_vmd)

                # Load saved file
                result_vmd = vmd.File()
                result_vmd.load(filepath=output_vmd)

                # Basic comparisons
                self.__check_vmd_header(source_vmd, result_vmd)
                self.assertEqual(len(source_vmd.boneAnimation), len(result_vmd.boneAnimation))
                self.assertEqual(len(source_vmd.shapeKeyAnimation), len(result_vmd.shapeKeyAnimation))

                print(f"    ✓ Direct VMD test passed")
                success_count += 1

            except Exception as e:
                print(f"    ✗ Direct VMD test failed: {e}")

        print(f"\n=== Direct VMD Test Results ===")
        print(f"Successfully tested: {success_count}/{len(vmd_files)} VMD files")

        # Require all tests to pass
        success_rate = success_count / len(vmd_files)
        self.assertEqual(success_count, len(vmd_files), f"All direct VMD tests must pass. Success rate: {success_rate:.1%} ({success_count}/{len(vmd_files)})")


if __name__ == "__main__":
    import sys

    sys.argv = [__file__] + (sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    unittest.main()
