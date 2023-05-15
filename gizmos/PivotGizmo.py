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
import bmesh
import mathutils
import math
from bl_ui.space_toolsystem_toolbar import (
    VIEW3D_PT_tools_active as view3d_tools
)
from bpy.types import (
    # WorkSpaceTool,
    # Operator,
    GizmoGroup,
)

def active_tool():
    return view3d_tools.tool_active_from_context(bpy.context)


def get_tools():
    return view3d_tools.tools_from_context(bpy.context)


# These constants are the indicies for the bounding box corners
# Bboxes are a pain to deal with, without them.

XNEG_YNEG_ZNEG = 0
XNEG_YNEG_ZPOS = 1
XNEG_YPOS_ZPOS = 2
XNEG_YPOS_ZNEG = 3
XPOS_YNEG_ZNEG = 4
XPOS_YNEG_ZPOS = 5
XPOS_YPOS_ZPOS = 6
XPOS_YPOS_ZNEG = 7

# Box faces

XPOS_FACE = (XPOS_YNEG_ZNEG, XPOS_YNEG_ZPOS, XPOS_YPOS_ZPOS, XPOS_YPOS_ZNEG)
XNEG_FACE = (XNEG_YNEG_ZNEG, XNEG_YNEG_ZPOS, XNEG_YPOS_ZPOS, XNEG_YPOS_ZNEG)

YPOS_FACE = (XNEG_YPOS_ZPOS, XNEG_YPOS_ZNEG, XPOS_YPOS_ZPOS, XPOS_YPOS_ZNEG)
YNEG_FACE = (XNEG_YNEG_ZNEG, XNEG_YNEG_ZPOS, XPOS_YNEG_ZNEG, XPOS_YNEG_ZPOS)

ZPOS_FACE = (XNEG_YNEG_ZPOS, XNEG_YPOS_ZPOS, XPOS_YNEG_ZPOS, XPOS_YPOS_ZPOS)
ZNEG_FACE = (XNEG_YNEG_ZNEG, XNEG_YPOS_ZNEG, XPOS_YNEG_ZNEG, XPOS_YPOS_ZNEG)

FACE_LIST = (XPOS_FACE, XNEG_FACE, YPOS_FACE, YNEG_FACE, ZPOS_FACE, ZNEG_FACE)


def get_center(lst, obj):
    """
    Returns the average of a list of values.\n
    Meant for averaging vector lists.
    """ 

    if isinstance(lst, tuple):
        v_sum = mathutils.Vector((0.0, 0.0, 0.0))

        for i in lst:
            v_sum += mathutils.Vector(obj.bound_box[i])

        return v_sum / float(len(lst))
    else:
        print("NOT A LIST")


def bbox_center(lst):
    v_sum = mathutils.Vector((0.0, 0.0, 0.0))

    for v in lst:
        v_sum += mathutils.Vector(v)

    return v_sum / float(len(lst))


class WLT_PivotGizmoGroup(GizmoGroup):
    bl_idname = "WLT_pivot_gizmo_group"
    bl_label = "WLT Pivot Gizmo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'SHOW_MODAL_ALL', 'SCALE'}

    @classmethod
    def poll(cls, context):
        if context.active_object and (context.active_object.type == 'MESH'):
            return True

    def setup(self, context):
        obj = context.active_object
        self.bounds = []
    
        self.corners = []
    
        self.faces = []

        for point in obj.bound_box:

            loc = mathutils.Vector(point)
            loc *= obj.matrix_world.to_scale()
            loc.rotate(obj.matrix_world.to_quaternion())
            loc += obj.location.copy()
            self.bounds.append(loc)

            corner = self.gizmos.new('GIZMO_GT_move_3d')
            corner.draw_options = {'ALIGN_VIEW', 'FILL'}
            corner.matrix_basis = mathutils.Matrix.Translation(loc)
            corner.scale_basis = 0.125
            corner.alpha = 0.05
            corner.alpha_highlight = 0.75
            self.corners.append(corner)

        for face in FACE_LIST:
            center = get_center(face, obj)
            center *= obj.matrix_world.to_scale()
            center.rotate(obj.matrix_world.to_quaternion())
            center += obj.location.copy()

            giz = self.gizmos.new('GIZMO_GT_move_3d')
            giz.draw_options = {'ALIGN_VIEW', 'FILL'}
            giz.matrix_basis = mathutils.Matrix.Translation(center)
            giz.scale_basis = 0.125
            giz.alpha = 0.05
            giz.alpha_highlight = 0.75

            self.faces.append(giz)


    def draw_prepare(self, context):
        obj = context.active_object
        self.bounds = []
        corners = self.corners
        faces = self.faces

        for i, point in enumerate(obj.bound_box):

            loc = mathutils.Vector(point)
            loc *= obj.matrix_world.to_scale()
            loc.rotate(obj.matrix_world.to_quaternion())
            loc += obj.location.copy()
            self.bounds.append(loc)

            corners[i].matrix_basis = mathutils.Matrix.Translation(loc)

        for i, face in enumerate(FACE_LIST):
            center = get_center(face, obj)
            center *= obj.matrix_world.to_scale()
            center.rotate(obj.matrix_world.to_quaternion())
            center += obj.location.copy()

            faces[i].matrix_basis = mathutils.Matrix.Translation(center)



        
