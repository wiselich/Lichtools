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
import mathutils
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatVectorProperty,
    IntVectorProperty
)

class WLT_OT_repack(bpy.types.Operator):
    bl_idname = "wlt.repack"
    bl_label = "WLT Repack"
    bl_description = "Currently toggles the viewport wireframe colors"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        node = context.active_node

        if not node.bl_idname == "ShaderNodeTexImage":
            return {'CANCELLED'}

        image = node.image

        image.filepath = "Q:\\Proj\\Rand\\Hole_2\\B.psd"

        print(image.filepath)

        bpy.context.area.tag_redraw()
        

        return {'FINISHED'}


class WLT_OT_copy_cursor_transform(bpy.types.Operator):
    bl_idname = "wlt.gnode_copy_cursor"
    bl_label = "WLT GNode Copy Cursor"
    bl_description = "Copies the transform from the 3D Cursor and pastes it into the selected node"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        obj = context.active_object
        if not obj.modifiers:
            return {'CANCELLED'}

        mod = obj.modifiers.active

        if not mod.type == 'NODES':
            return {'CANCELLED'}

        graph = mod.node_group
        active_node = graph.nodes.active

        cursor = context.scene.cursor

        if active_node:
            if not active_node.bl_idname == "GeometryNodeTransform":
                return {'CANCELLED'}

            active_node.inputs[1].default_value = cursor.location
            active_node.inputs[2].default_value = cursor.rotation_euler

        return {'FINISHED'}
            
OUT = [
    WLT_OT_repack,
    WLT_OT_copy_cursor_transform
]
