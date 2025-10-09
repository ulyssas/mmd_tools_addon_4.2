# Copyright 2025 MMD Tools authors
# This file is part of MMD Tools.

"""
Simplest compatibility layer for Action.

Only the first channelbag of ActionChannelbag is used,
preserving the behavior of the previous version.
Although ActionChannelbag was introduced in Blender 4.4,
since MMD Tools works well in 4.2–4.5, use it only in Blender 5.0+.
"""

# TODO: Support all Action API changes in Blender 5.0+

import bpy

IS_BLENDER_50_UP = bpy.app.version >= (5, 0)

if IS_BLENDER_50_UP:
    FCurvesCollection = bpy.types.ActionChannelbagFCurves
else:
    FCurvesCollection = bpy.types.ActionFCurves
