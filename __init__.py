# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from time import perf_counter
from . import (
    operators,
    ui,
    gizmos,
    properties,
    singletons
    )

from . preferences import WLTAddonPreferences

# Blender uses the package name, instead of the add-on name, for keying things
# like add-on preferences. And, since there are edge cases where the package
# name isn't deterministic,
__package__ = "WLT"

bl_info = {
    "name": "WLT",
    "author": "Asher",
    "description": "Wise Lich Toolbox",
    "blender": (3, 4, 0),
    "version": (0, 8, 2),
    "location": "View3D",
    "warning": "Alpha of all Alphas",
    "category": "Modeling"
}

def register():
    start = perf_counter()
    bpy.utils.register_class(WLTAddonPreferences)
    operators.register()
    ui.register()
    gizmos.register()
    properties.register()
    singletons.register()

    stop = perf_counter()
    print(f"WLT Startup Time: {stop - start}")


def unregister():
    bpy.utils.unregister_class(WLTAddonPreferences)

    operators.unregister()
    ui.unregister()
    gizmos.unregister()
    properties.unregister()

    singletons.unregister()