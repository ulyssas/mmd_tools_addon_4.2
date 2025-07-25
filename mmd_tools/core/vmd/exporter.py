# Copyright 2016 MMD Tools authors
# This file is part of MMD Tools.

import logging
import math
import re
from typing import List, Optional, Set

import bpy
from mathutils import Euler, Quaternion

from .. import vmd
from ..camera import MMDCamera
from ..lamp import MMDLamp
from ..vmd.importer import _FnBezier


class _FCurve:
    @staticmethod
    def __x_co_0(x: bpy.types.Keyframe):
        return x.co[0]

    def __init__(self, default_value, preserve_curves=False):
        self.__default_value = default_value
        self.__fcurve: Optional[bpy.types.FCurve] = None
        self.__sorted_keyframe_points: Optional[List[bpy.types.Keyframe]] = None
        self.__preserve_curves = preserve_curves

    def setFCurve(self, fcurve: bpy.types.FCurve):
        assert fcurve.is_valid and self.__fcurve is None
        self.__fcurve = fcurve
        self.__sorted_keyframe_points: List[bpy.types.Keyframe] = sorted(self.__fcurve.keyframe_points, key=self.__x_co_0)

    def set_preserve_curves(self, value):
        self.__preserve_curves = value

    def frameNumbers(self):
        sorted_keyframe_points = self.__sorted_keyframe_points
        result: Set[int] = set()
        if sorted_keyframe_points is None:
            return result

        if len(sorted_keyframe_points) == 0:
            return result

        kp1 = sorted_keyframe_points[0]
        result.add(round(kp1.co[0]))

        kp0 = kp1
        for kp1 in sorted_keyframe_points[1:]:
            result.add(round(kp1.co[0]))
            if self.__preserve_curves and kp0.interpolation != "LINEAR" and kp1.co.x - kp0.co.x > 2.5:
                if kp0.interpolation == "CONSTANT":
                    result.add(max(0, round(kp1.co[0]) - 1))
                elif kp0.interpolation == "BEZIER":
                    bz = _FnBezier.from_fcurve(kp0, kp1)
                    result.update(round(bz.evaluate(t).x) for t in bz.find_critical())
            kp0 = kp1

        return result

    @staticmethod
    def getVMDControlPoints(kp0, kp1):
        if kp0.interpolation == "BEZIER":
            return _FCurve.__toVMDControlPoints(_FnBezier.from_fcurve(kp0, kp1))
        return ((20, 20), (107, 107))

    @staticmethod
    def __toVMDControlPoints(bezier):
        p0, p1, p2, p3 = bezier.points
        dx, dy = p3 - p0
        x1, y1 = p1 - p0
        x2, y2 = p2 - p0

        # When dy is too small, restoring (y1, y2) is impossible and the curve is meaningless in MMD
        if abs(dy) < 1e-4:
            return ((20, 20), (107, 107))
        y1 = max(0, min(127, round(y1 * 127.0 / dy)))
        y2 = max(0, min(127, round(y2 * 127.0 / dy)))
        if abs(dx) < 1e-4:
            (x1, x2) = (20, 107)
        else:
            x1 = max(0, min(127, round(x1 * 127.0 / dx)))
            x2 = max(0, min(127, round(x2 * 127.0 / dx)))
        return ((x1, y1), (x2, y2))

    def sampleFrames(self, frame_numbers: List[int]):
        # assume set(frame_numbers) & set(self.frameNumbers()) == set(self.frameNumbers())
        fcurve = self.__fcurve
        if fcurve is None or len(fcurve.keyframe_points) == 0:  # no key frames
            return [[self.__default_value, ((20, 20), (107, 107))] for _ in frame_numbers]

        result = []

        evaluate = fcurve.evaluate
        frame_iter = iter(frame_numbers)
        prev_kp = None
        prev_i = None
        kp: bpy.types.Keyframe
        for kp in self.__sorted_keyframe_points:
            i = round(kp.co[0])
            if i == prev_i:
                prev_kp = kp
                continue
            prev_i = i
            frames = []
            while True:
                frame = next(frame_iter)
                frames.append(frame)
                if frame >= i:
                    break
            assert len(frames) >= 1 and frames[-1] == i
            if prev_kp is None:
                # starting key frames
                result.extend([kp.co[1], ((20, 20), (107, 107))] for f in frames)
            elif len(frames) == 1:
                result.append([kp.co[1], self.getVMDControlPoints(prev_kp, kp)])
            elif prev_kp.interpolation == "BEZIER":
                bz = _FnBezier.from_fcurve(prev_kp, kp)
                for f in frames[:-1]:
                    b1, bz, pt = bz.split_by_x(f)
                    result.append([pt.y, self.__toVMDControlPoints(b1)])
                result.append([bz.points[-1].y, self.__toVMDControlPoints(bz)])
            else:
                result.extend([evaluate(f), ((20, 20), (107, 107))] for f in frames)
            prev_kp = kp

        prev_kp_co_1 = prev_kp.co[1]
        result.extend([[prev_kp_co_1, ((20, 20), (107, 107))] for _ in frame_iter])

        return result


class VMDExporter:
    def __init__(self):
        self.__scale = 1
        self.__frame_start = min(1, bpy.context.scene.frame_start)  # handle frame_start == 0
        self.__frame_end = float("inf")
        self.__bone_converter_cls = vmd.importer.BoneConverter
        self.__ik_fcurves = {}
        self.__preserve_curves = False

    def __allFrameKeys(self, curves: List[_FCurve]):
        all_frames = set()
        for i in curves:
            i.set_preserve_curves(self.__preserve_curves)
            all_frames |= i.frameNumbers()

        if len(all_frames) == 0:
            return

        frame_start = min(all_frames)
        if frame_start != self.__frame_start:
            frame_start = self.__frame_start
            all_frames.add(frame_start)

        frame_end = max(all_frames)
        if frame_end > self.__frame_end:
            frame_end = self.__frame_end
            all_frames.add(frame_end)

        all_frames = sorted(all_frames)
        all_keys = [i.sampleFrames(all_frames) for i in curves]
        # return zip(all_frames, *all_keys)
        for data in zip(all_frames, *all_keys, strict=False):
            frame_number = data[0]
            if frame_number < frame_start:
                continue
            if frame_number > frame_end:
                break
            yield data

    @staticmethod
    def __minRotationDiff(prev_q, curr_q):
        t1 = (prev_q.w - curr_q.w) ** 2 + (prev_q.x - curr_q.x) ** 2 + (prev_q.y - curr_q.y) ** 2 + (prev_q.z - curr_q.z) ** 2
        t2 = (prev_q.w + curr_q.w) ** 2 + (prev_q.x + curr_q.x) ** 2 + (prev_q.y + curr_q.y) ** 2 + (prev_q.z + curr_q.z) ** 2
        # t1 = prev_q.rotation_difference(curr_q).angle
        # t2 = prev_q.rotation_difference(-curr_q).angle
        return -curr_q if t2 < t1 else curr_q

    @staticmethod
    def __getVMDBoneInterpolation(x_axis, y_axis, z_axis, rotation):
        x_x1, x_y1 = x_axis[0]
        x_x2, x_y2 = x_axis[1]
        y_x1, y_y1 = y_axis[0]
        y_x2, y_y2 = y_axis[1]
        z_x1, z_y1 = z_axis[0]
        z_x2, z_y2 = z_axis[1]
        r_x1, r_y1 = rotation[0]
        r_x2, r_y2 = rotation[1]
        # fmt: off
        # return [ # minimum acceptable data
        #    x_x1, 0, 0, 0, x_y1, 0, 0, 0, x_x2, 0, 0, 0, x_y2, 0, 0, 0,
        #    y_x1, 0, 0, 0, y_y1, 0, 0, 0, y_x2, 0, 0, 0, y_y2, 0, 0, 0,
        #    z_x1, 0, 0, 0, z_y1, 0, 0, 0, z_x2, 0, 0, 0, z_y2, 0, 0, 0,
        #    r_x1, 0, 0, 0, r_y1, 0, 0, 0, r_x2, 0, 0, 0, r_y2, 0, 0, 0,
        #    ]
        return [  # full data, indices in [2, 3, 31, 46, 47, 61, 62, 63] are unclear
            x_x1, y_x1,    0,    0, x_y1, y_y1, z_y1, r_y1, x_x2, y_x2, z_x2, r_x2, x_y2, y_y2, z_y2, r_y2,
            y_x1, z_x1, r_x1, x_y1, y_y1, z_y1, r_y1, x_x2, y_x2, z_x2, r_x2, x_y2, y_y2, z_y2, r_y2,    0,
            z_x1, r_x1, x_y1, y_y1, z_y1, r_y1, x_x2, y_x2, z_x2, r_x2, x_y2, y_y2, z_y2, r_y2,    0,    0,
            r_x1, x_y1, y_y1, z_y1, r_y1, x_x2, y_x2, z_x2, r_x2, x_y2, y_y2, z_y2, r_y2,    0,    0,    0,
        ]
        # fmt: on

    @staticmethod
    def __pickRotationInterpolation(rotation_interps):
        for ir in rotation_interps:
            if ir != ((20, 20), (107, 107)):
                return ir
        return ((20, 20), (107, 107))

    @staticmethod
    def __xyzw_from_rotation_mode(mode):
        if mode == "QUATERNION":
            return lambda xyzw: xyzw

        if mode == "AXIS_ANGLE":

            def __xyzw_from_axis_angle(xyzw):
                q = Quaternion(xyzw[:3], xyzw[3])
                return [q.x, q.y, q.z, q.w]

            return __xyzw_from_axis_angle

        def __xyzw_from_euler(xyzw):
            q = Euler(xyzw[:3], xyzw[3]).to_quaternion()
            return [q.x, q.y, q.z, q.w]

        return __xyzw_from_euler

    def __exportBoneAnimation(self, armObj):
        if armObj is None:
            return None
        animation_data = armObj.animation_data
        if animation_data is None or animation_data.action is None:
            logging.warning('[WARNING] armature "%s" has no animation data', armObj.name)
            return None

        vmd_bone_anim = vmd.BoneAnimation()

        anim_bones = {}
        rePath = re.compile(r'^pose\.bones\["(.+)"\]\.([a-z_]+)$')
        prop_rotation_map = {"QUATERNION": "rotation_quaternion", "AXIS_ANGLE": "rotation_axis_angle"}
        for fcurve in animation_data.action.fcurves:
            m = rePath.match(fcurve.data_path)
            if m is None:
                continue
            bone = armObj.pose.bones.get(m.group(1), None)
            if bone is None:
                logging.warning(" * Bone not found: %s", m.group(1))
                continue
            if bone.is_mmd_shadow_bone:
                continue
            prop_name = m.group(2)
            if prop_name == "mmd_ik_toggle":
                self.__ik_fcurves[bone] = fcurve
                continue
            if prop_name not in {"location", prop_rotation_map.get(bone.rotation_mode, "rotation_euler")}:
                continue

            if bone not in anim_bones:
                data = list(bone.location)
                if bone.rotation_mode == "QUATERNION":
                    data += list(bone.rotation_quaternion)
                elif bone.rotation_mode == "AXIS_ANGLE":
                    data += list(bone.rotation_axis_angle)
                else:
                    data += [bone.rotation_mode] + list(bone.rotation_euler)
                anim_bones[bone] = [_FCurve(i) for i in data]  # x, y, z, rw, rx, ry, rz
            bone_curves = anim_bones[bone]
            if prop_name == "location":  # x, y, z
                bone_curves[fcurve.array_index].setFCurve(fcurve)
            elif prop_name == "rotation_quaternion":  # rw, rx, ry, rz
                bone_curves[3 + fcurve.array_index].setFCurve(fcurve)
            elif prop_name == "rotation_axis_angle":  # rw, rx, ry, rz
                bone_curves[3 + fcurve.array_index].setFCurve(fcurve)
            elif prop_name == "rotation_euler":  # mode, rx, ry, rz
                bone_curves[3 + fcurve.array_index + 1].setFCurve(fcurve)

        for bone, bone_curves in anim_bones.items():
            key_name = bone.mmd_bone.name_j or bone.name
            if key_name in vmd_bone_anim:
                raise ValueError(f"VMD bone name {key_name} collision")

            frame_keys = vmd_bone_anim[key_name]

            get_xyzw = self.__xyzw_from_rotation_mode(bone.rotation_mode)
            converter = self.__bone_converter_cls(bone, self.__scale, invert=True)
            prev_rot = None
            for frame_number, x, y, z, rw, rx, ry, rz in self.__allFrameKeys(bone_curves):
                key = vmd.BoneFrameKey()
                key.frame_number = frame_number - self.__frame_start
                key.location = converter.convert_location([x[0], y[0], z[0]])
                curr_rot = converter.convert_rotation(get_xyzw([rx[0], ry[0], rz[0], rw[0]]))
                if prev_rot is not None:
                    curr_rot = self.__minRotationDiff(prev_rot, curr_rot)
                prev_rot = curr_rot
                key.rotation = curr_rot[1:] + curr_rot[0:1]  # (w, x, y, z) to (x, y, z, w)
                # FIXME we can only choose one interpolation from (rw, rx, ry, rz) for bone's rotation
                ir = self.__pickRotationInterpolation([rw[1], rx[1], ry[1], rz[1]])
                ix, iy, iz = converter.convert_interpolation([x[1], y[1], z[1]])
                key.interp = self.__getVMDBoneInterpolation(ix, iy, iz, ir)
                frame_keys.append(key)
            logging.info("(bone) frames:%5d  name: %s", len(frame_keys), key_name)
        logging.info("---- bone animations:%5d  source: %s", len(vmd_bone_anim), armObj.name)
        return vmd_bone_anim

    def __exportMorphAnimation(self, meshObj):
        if meshObj is None:
            return None
        if meshObj.data.shape_keys is None:
            logging.warning('[WARNING] mesh "%s" has no shape keys', meshObj.name)
            return None
        animation_data = meshObj.data.shape_keys.animation_data
        if animation_data is None or animation_data.action is None:
            logging.warning('[WARNING] mesh "%s" has no animation data', meshObj.name)
            return None

        vmd_morph_anim = vmd.ShapeKeyAnimation()

        key_blocks = meshObj.data.shape_keys.key_blocks

        def __get_key_block(key):
            if key.isdigit():
                try:
                    return key_blocks[int(key)]
                except IndexError:
                    return None
            return key_blocks.get(eval(key), None)

        rePath = re.compile(r"^key_blocks\[(.+)\]\.value$")
        for fcurve in animation_data.action.fcurves:
            m = rePath.match(fcurve.data_path)
            if m is None:
                continue

            key_name = m.group(1)
            kb = __get_key_block(key_name)
            if kb is None:
                logging.warning(" * Shape key not found: %s", key_name)
                continue

            key_name = kb.name
            assert key_name not in vmd_morph_anim
            anim = vmd_morph_anim[key_name]

            curve = _FCurve(kb.value)
            curve.setFCurve(fcurve)

            for frame_number, weight in self.__allFrameKeys([curve]):
                key = vmd.ShapeKeyFrameKey()
                key.frame_number = frame_number - self.__frame_start
                key.weight = weight[0]
                anim.append(key)
            logging.info("(mesh) frames:%5d  name: %s", len(anim), key_name)
        logging.info("---- morph animations:%5d  source: %s", len(vmd_morph_anim), meshObj.name)
        return vmd_morph_anim

    def __exportPropertyAnimation(self, armObj):
        if armObj is None:
            return None

        vmd_prop_anim = vmd.PropertyAnimation()

        prop_curves = [_FCurve(True)]  # visible, IKn

        root = armObj.parent
        if getattr(root, "mmd_type", None) == "ROOT":
            animation_data = root.animation_data
            if animation_data and animation_data.action:
                for fcurve in animation_data.action.fcurves:
                    if fcurve.data_path == "mmd_root.show_meshes":
                        prop_curves[0].setFCurve(fcurve)
                        break

        ik_name_list = []
        for bone, fcurve in self.__ik_fcurves.items():
            c = _FCurve(True)
            c.setFCurve(fcurve)
            prop_curves.append(c)
            ik_name_list.append(bone.mmd_bone.name_j or bone.name)

        for data in self.__allFrameKeys(prop_curves):
            key = vmd.PropertyFrameKey()
            key.frame_number = data[0] - self.__frame_start
            key.visible = round(data[1][0])
            key.ik_states = [(ik_name, round(on_off[0])) for ik_name, on_off in zip(ik_name_list, data[2:], strict=False)]
            vmd_prop_anim.append(key)
        logging.info("(property) frames:%5d  name: %s", len(vmd_prop_anim), root.name if root else armObj.name)
        return vmd_prop_anim

    def __exportCameraAnimation(self, cameraObj):
        if cameraObj is None:
            return None
        if not MMDCamera.isMMDCamera(cameraObj):
            logging.warning('[WARNING] camera "%s" is not MMDCamera', cameraObj.name)
            return None

        cam_rig = MMDCamera(cameraObj)
        mmd_cam = cam_rig.object()
        camera = cam_rig.camera()

        vmd_cam_anim = vmd.CameraAnimation()

        data = list(mmd_cam.location) + list(mmd_cam.rotation_euler)
        data.append(mmd_cam.mmd_camera.angle)
        data.append(mmd_cam.mmd_camera.is_perspective)
        data.append(camera.location.y)
        cam_curves = [_FCurve(i) for i in data]  # x, y, z, rx, ry, rz, fov, persp, distance

        animation_data = mmd_cam.animation_data
        if animation_data and animation_data.action:
            for fcurve in animation_data.action.fcurves:
                if fcurve.data_path == "location":  # x, y, z
                    cam_curves[fcurve.array_index].setFCurve(fcurve)
                elif fcurve.data_path == "rotation_euler":  # rx, ry, rz
                    cam_curves[3 + fcurve.array_index].setFCurve(fcurve)
                elif fcurve.data_path == "mmd_camera.angle":  # fov
                    cam_curves[6].setFCurve(fcurve)
                elif fcurve.data_path == "mmd_camera.is_perspective":  # persp
                    cam_curves[7].setFCurve(fcurve)

        animation_data = camera.animation_data
        if animation_data and animation_data.action:
            for fcurve in animation_data.action.fcurves:
                if fcurve.data_path == "location" and fcurve.array_index == 1:  # distance
                    cam_curves[8].setFCurve(fcurve)

        for frame_number, x, y, z, rx, ry, rz, fov, persp, distance in self.__allFrameKeys(cam_curves):
            key = vmd.CameraKeyFrameKey()
            key.frame_number = frame_number - self.__frame_start
            key.location = [x[0] * self.__scale, z[0] * self.__scale, y[0] * self.__scale]
            key.rotation = [rx[0], rz[0], ry[0]]  # euler
            key.angle = round(math.degrees(fov[0]))
            key.distance = distance[0] * self.__scale
            key.persp = bool(persp[0])

            # FIXME we can only choose one interpolation from (rx, ry, rz) for camera's rotation
            ir = self.__pickRotationInterpolation([rx[1], ry[1], rz[1]])
            ix, iy, iz, iD, iF = x[1], z[1], y[1], distance[1], fov[1]
            # fmt: off
            key.interp = [
                ix[0][0], ix[1][0], ix[0][1], ix[1][1],
                iy[0][0], iy[1][0], iy[0][1], iy[1][1],
                iz[0][0], iz[1][0], iz[0][1], iz[1][1],
                ir[0][0], ir[1][0], ir[0][1], ir[1][1],
                iD[0][0], iD[1][0], iD[0][1], iD[1][1],
                iF[0][0], iF[1][0], iF[0][1], iF[1][1],
            ]
            # fmt: on

            vmd_cam_anim.append(key)
        logging.info("(camera) frames:%5d  name: %s", len(vmd_cam_anim), mmd_cam.name)
        return vmd_cam_anim

    def __exportLampAnimation(self, lampObj):
        if lampObj is None:
            return None
        if not MMDLamp.isMMDLamp(lampObj):
            logging.warning('[WARNING] lamp "%s" is not MMDLamp', lampObj.name)
            return None

        lamp_rig = MMDLamp(lampObj)
        mmd_lamp = lamp_rig.object()
        lamp = lamp_rig.lamp()

        vmd_lamp_anim = vmd.LampAnimation()

        data = list(lamp.data.color) + list(lamp.location)
        lamp_curves = [_FCurve(i) for i in data]  # r, g, b, x, y, z

        animation_data = lamp.data.animation_data
        if animation_data and animation_data.action:
            for fcurve in animation_data.action.fcurves:
                if fcurve.data_path == "color":  # r, g, b
                    lamp_curves[fcurve.array_index].setFCurve(fcurve)

        animation_data = lamp.animation_data
        if animation_data and animation_data.action:
            for fcurve in animation_data.action.fcurves:
                if fcurve.data_path == "location":  # x, y, z
                    lamp_curves[3 + fcurve.array_index].setFCurve(fcurve)

        for frame_number, r, g, b, x, y, z in self.__allFrameKeys(lamp_curves):
            key = vmd.LampKeyFrameKey()
            key.frame_number = frame_number - self.__frame_start
            key.color = [r[0], g[0], b[0]]
            key.direction = [-x[0], -z[0], -y[0]]
            vmd_lamp_anim.append(key)
        logging.info("(lamp) frames:%5d  name: %s", len(vmd_lamp_anim), mmd_lamp.name)
        return vmd_lamp_anim

    def export(self, **args):
        armature = args.get("armature")
        mesh = args.get("mesh")
        camera = args.get("camera")
        lamp = args.get("lamp")
        filepath = args.get("filepath", "")

        self.__scale = args.get("scale", 1.0)

        if args.get("use_frame_range", False):
            self.__frame_start = bpy.context.scene.frame_start
            self.__frame_end = bpy.context.scene.frame_end

        if args.get("use_pose_mode", False):
            self.__bone_converter_cls = vmd.importer.BoneConverterPoseMode

        self.__preserve_curves = args.get("preserve_curves", False)

        if armature or mesh:
            vmdFile = vmd.File()
            vmdFile.header = vmd.Header()
            vmdFile.header.model_name = args.get("model_name", "")
            vmdFile.boneAnimation = self.__exportBoneAnimation(armature)
            vmdFile.shapeKeyAnimation = self.__exportMorphAnimation(mesh)
            vmdFile.propertyAnimation = self.__exportPropertyAnimation(armature)
            vmdFile.save(filepath=filepath)

        elif camera or lamp:
            vmdFile = vmd.File()
            vmdFile.header = vmd.Header()
            vmdFile.header.model_name = "カメラ・照明"
            vmdFile.cameraAnimation = self.__exportCameraAnimation(camera)
            vmdFile.lampAnimation = self.__exportLampAnimation(lamp)
            vmdFile.save(filepath=filepath)
