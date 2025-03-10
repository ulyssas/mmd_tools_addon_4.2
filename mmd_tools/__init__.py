# -*- coding: utf-8 -*-
# Copyright 2012 MMD Tools authors
# This file is part of MMD Tools.

# MMD Tools is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# MMD Tools is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


bl_info = {
    "name": "mmd_tools",
    "author": "UuuNyaa <uuunyaa@gmail.com>",
    "version": (4, 3, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > MMD Panel",
    "description": "Utility tools for MMD model editing. (UuuNyaa's forked version)",
    "warning": "",
    "doc_url": "https://mmd-blender.fandom.com/wiki/MMD_Tools",
    "wiki_url": "https://mmd-blender.fandom.com/wiki/MMD_Tools",
    "tracker_url": "https://github.com/UuuNyaa/blender_mmd_tools/issues",
    "support": "COMMUNITY",
    "category": "Object",
}

MMD_TOOLS_VERSION = ".".join(map(str, bl_info["version"]))

import os

PACKAGE_NAME = __package__
PACKAGE_PATH = os.path.dirname(__file__)


from . import auto_load

auto_load.init(PACKAGE_NAME)


def register():
    import bpy

    import mmd_tools.handlers

    mmd_tools.auto_load.register()

    # pylint: disable=import-outside-toplevel
    from mmd_tools.m17n import translation_dict

    bpy.app.translations.register(bl_info["name"], translation_dict)

    mmd_tools.handlers.MMDHanders.register()


def unregister():
    import bpy

    import mmd_tools.handlers

    mmd_tools.handlers.MMDHanders.unregister()

    bpy.app.translations.unregister(bl_info["name"])

    mmd_tools.auto_load.unregister()


if __name__ == "__main__":
    register()