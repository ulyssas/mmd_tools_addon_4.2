# Copyright 2013 MMD Tools authors
# This file is part of MMD Tools.

import bpy


def setupFrameRanges():
    s, e = 1, 1
    for action in bpy.data.actions:
        # Blend frame ranges from two imported VMD files
        # Get first imported VMD range
        action.use_frame_range = True
        ts, te = action.frame_range
        s, e = min(s, ts), max(e, te)
        # Get second imported VMD range
        action.use_frame_range = False
        ts, te = action.frame_range
        s, e = min(s, ts), max(e, te)
    bpy.context.scene.frame_start = int(s)
    bpy.context.scene.frame_end = int(e)
    if bpy.context.scene.rigidbody_world is not None:
        bpy.context.scene.rigidbody_world.point_cache.frame_start = int(s)
        bpy.context.scene.rigidbody_world.point_cache.frame_end = int(e)


def setupLighting():
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.use_environment_light = True
    bpy.context.scene.world.light_settings.use_indirect_light = True


def setupFps():
    bpy.context.scene.render.fps = 30
    bpy.context.scene.render.fps_base = 1
