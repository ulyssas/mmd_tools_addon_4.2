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

import os

from . import auto_load

PACKAGE_NAME = __package__
PACKAGE_PATH = os.path.dirname(__file__)

bl_info = {
    "name": "mmd_tools",
    "author": "UuuNyaa <uuunyaa@gmail.com>",
    "version": (4, 5, 3),
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

auto_load.init(PACKAGE_NAME)


def register():
    import bpy

    from . import handlers

    auto_load.register()

    # pylint: disable=import-outside-toplevel
    from .m17n import translations_dict

    bpy.app.translations.register(PACKAGE_NAME, translations_dict)

    handlers.MMDHanders.register()


def unregister():
    import bpy

    from . import handlers

    handlers.MMDHanders.unregister()

    bpy.app.translations.unregister(PACKAGE_NAME)

    auto_load.unregister()


if __name__ == "__main__":
    register()
