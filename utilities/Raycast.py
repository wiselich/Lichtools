# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Hell is other people's code.

import bpy
import bpy_extras
from bpy_extras.view3d_utils import region_2d_to_origin_3d
import mathutils
from mathutils import Vector

def build_mouse_vec(region, rv3d, loc_2d):

    view_vec = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, rv3d, loc_2d)
    ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, loc_2d)
    ray_target = ray_origin + (view_vec * 10000000000000)
    ray_vec = ray_target - ray_origin

    return (ray_origin, ray_vec)


# So this does the opposite of raycasting. Instead of creating a vector from a 2D location,
# it creates an array of 2d locations from an array of 3d vectors
def deproject(region, rv3d, points):
    screenpoints = []

    for loc in points:
        point = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, loc)
        screenpoints.append(point)
    
    return screenpoints