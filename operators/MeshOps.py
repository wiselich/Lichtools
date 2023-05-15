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
import numpy
import math
from bpy.props import (
    FloatVectorProperty,
    FloatProperty,
    EnumProperty,
    BoolProperty, StringProperty
)

class WLT_OT_MergeGeometry(bpy.types.Operator):
    """A wrapper for mesh merge that does funny things"""
    bl_idname = "wlt.merge"
    bl_label = "WLT Quick Symmetry"
    bl_description = "A wrapper for the mesh merge operator"
    bl_options = {'UNDO_GROUPED'}

    modes = [
        ("FIRST", "First", "", 1),
        ("LAST", "Last", "", 2),
        ("CENTER", "Center", "", 3),
        ("CURSOR", "3D Cursor", "", 4),
        ("COLLAPSE", "Collapse", "", 5),
    ]

    mode: EnumProperty(
        items=modes,
        name="Mode",
        description="How to hoop the scoop",
        default='LAST'
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.mode == 'EDIT_MESH'

    def execute(self, context):
        if context.scene.tool_settings.mesh_select_mode[0]:
            # target = 'VERTS'
            bpy.ops.mesh.merge('EXEC_DEFAULT', False, mode=self.mode)
        elif context.scene.tool_settings.mesh_select_mode[1]:
            # target = 'EDGES'
            if self.mode in {'FIRST', 'LAST'}:
                bpy.ops.mesh.merge('EXEC_DEFAULT', False, mode='COLLAPSE')
        elif context.scene.tool_settings.mesh_select_mode[2]:
            # target = 'FACES'
            if self.mode in {'FIRST', 'LAST'}:
                bpy.ops.mesh.merge('EXEC_DEFAULT', False, mode='COLLAPSE')

        return {'FINISHED'}

class WLT_OT_QuickSymmetry(bpy.types.Operator):
    """A wrapper for the symmetrize operator with an (optional) modal gizmo"""
    bl_idname = "wlt.quick_symmetry"
    bl_label = "WLT Quick Symmetry"
    bl_description = "A wrapper for the symmetrize operator with an (optional) modal gizmo"
    bl_options = {'UNDO_GROUPED'}

    axes = [
        ("POSITIVE_Z", "Z+", "", 1),
        ("NEGATIVE_Z", "Z-", "", 2),
        ("POSITIVE_Y", "Y+", "", 3),
        ("NEGATIVE_Y", "Y-", "", 4),
        ("POSITIVE_X", "X+", "", 5),
        ("NEGATIVE_X", "X-", "", 6),
    ]

    mirror_axis: EnumProperty(
        items=axes,
        name="Axis",
        description="Which axis to mirror",
        default='POSITIVE_Z'
    )

    do_modal: BoolProperty(
        name="Do Modal",
        default=True
    )

    use_cursor: BoolProperty(
        name="Use Cursor Orientation",
        default=False
    )

    def modal(self, context, event):

        if bpy.context.gizmo_group:
            print(bpy.context.gizmo_group.bl_idname)

        if bpy.context.workspace.WLT.modal_state.mirror_modal == False:
            context.area.header_text_set(None)
            bpy.context.window_manager.gizmo_group_type_unlink_delayed("WLT_mirror_gizmo_group")
            return {'FINISHED'}

        if (event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT', 'SPACE'}) and (event.value == 'PRESS'):
            bpy.context.workspace.WLT.modal_state.mm_use_cursor = True
            bpy.context.area.tag_redraw()

        if (event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT', 'SPACE'}) and (event.value == 'RELEASE'):
            bpy.context.workspace.WLT.modal_state.mm_use_cursor = False
            bpy.context.area.tag_redraw()

        if event.type in {'LEFTMOUSE', 'MIDDLEMOUSE', 'MOUSEMOVE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            if event.value == 'CLICK':
                if bpy.context.workspace.WLT.modal_state.mirror_modal == False:
                    return {'PASS_THROUGH', 'FINISHED'}
            return {'PASS_THROUGH'}

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set(None)
            bpy.context.window_manager.gizmo_group_type_unlink_delayed("WLT_mirror_gizmo_group")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        bpy.context.workspace.WLT.modal_state.mm_use_cursor = False
        do_mode = True if bpy.context.mode == 'EDIT_MESH' else False

        if event.shift:
            self.use_cursor = True

        if self.do_modal:
            context.area.header_text_set("In WLT Mirror Modal, Press Esc to Exit")

            bpy.context.workspace.WLT.modal_state.mirror_modal = True

            bpy.context.window_manager.gizmo_group_type_ensure("WLT_mirror_gizmo_group")

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            if self.use_cursor:
                if not bpy.context.mode == 'OBJECT':
                    bpy.ops.object.editmode_toggle('EXEC_DEFAULT', False)

                bpy.ops.transform.create_orientation(
                                'EXEC_DEFAULT',
                                False,
                                name="_TEMPSYM",
                                use=False,
                                use_view=False)

                context.scene.tool_settings.use_transform_data_origin = True
                bpy.ops.transform.transform('EXEC_DEFAULT', False, mode='ALIGN', orient_type='CURSOR')
                context.scene.tool_settings.use_transform_data_origin = False

            if bpy.context.mode == 'OBJECT':
                bpy.ops.object.editmode_toggle('EXEC_DEFAULT', False)

            bpy.ops.mesh.select_all('EXEC_DEFAULT', False, action='SELECT')
            bpy.ops.mesh.symmetrize('EXEC_DEFAULT', False, direction=self.mirror_axis)
            bpy.ops.mesh.select_all('EXEC_DEFAULT', False, action='DESELECT')

            bpy.context.workspace.WLT.modal_state.mirror_modal = False
            context.area.header_text_set(None)

            if self.use_cursor:
                if not bpy.context.mode == 'OBJECT':
                    bpy.ops.object.editmode_toggle('EXEC_DEFAULT', False)

                context.scene.tool_settings.use_transform_data_origin = True
                bpy.ops.transform.transform('EXEC_DEFAULT', False, mode='ALIGN', orient_type='_TEMPSYM')
                context.scene.tool_settings.use_transform_data_origin = False

                bpy.context.scene.transform_orientation_slots[0].type = '_TEMPSYM'
                bpy.ops.transform.delete_orientation('EXEC_DEFAULT', False)

                if do_mode:
                    bpy.ops.object.editmode_toggle('EXEC_DEFAULT', False)
            return {'FINISHED'}


class WLT_OT_LinearizeWeights(bpy.types.Operator):
    """This be some experimental stuff"""
    bl_idname = "wlt.linearize_weight"
    bl_label = "WLT Linearize Weight"
    bl_description = ("Sets the vertex weight of your current selection" +
                      " using a linear distance-based falloff")

    min_weight: FloatProperty(
        name="Minimum Weight",
        description="The search radius to find objects in",
        default=0.0,
    )

    max_weight: FloatProperty(
        name="Max Weight",
        description="The search radius to find objects in",
        default=1.0,
    )

    vertex_group: StringProperty(
        name="Vertex Group",
        default="Group"
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.mode == 'EDIT_MESH'

    # @classmethod
    # def description(cls, context, properties):
    #     return "NO"

    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        debug = False
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = [v for v in bm.verts if v.select]

        target_group = None
        for group in obj.vertex_groups:
            if group.name == self.vertex_group:
                target_group = group
                break
    
        if len(bm.select_history) == len(selected_verts):
            step = (self.max_weight - self.min_weight)/len(bm.select_history)
            target_list = bm.select_history
        else:
            step = (self.max_weight - self.min_weight)/len(selected_verts)
            start = bm.select_history.active

            distances = []
            for vert in selected_verts:
                if vert.index == start.index:
                    pass
                distances.append( [numpy.linalg.norm(start.co - vert.co), vert.index] )

            distances.sort(key = lambda x:float(x[0]), reverse=True)
            target_list = [ bm.verts[index[1]] for index in distances]

        do = []
        for i, v in enumerate(target_list):
            if v.select:
                do.append( ([v.index], i*step) )

        if target_group:
            bpy.ops.object.editmode_toggle('EXEC_DEFAULT', False)
            for action in do:
                target_group.add(action[0], action[1], 'REPLACE')

            bpy.ops.object.editmode_toggle('EXEC_DEFAULT', False)

            if debug:
                print("DONE")
        else:
            if debug:
                print("NO GROUP")
        
        return {'FINISHED'}


class WLT_OT_AngleShear(bpy.types.Operator):
    """Handles the 1/tan(radians(90-X)) input, with significantly less bullshit involved"""
    bl_idname = "wlt.angle_shear"
    bl_label = "WLT Angle Shear"
    bl_description = "A wrapper for the Shear operator that accepts an angle-based input"
    bl_options = {'REGISTER', 'UNDO'}


    angle: FloatProperty(
        name="Angle",
        default=0.10472,
        min=0.0,
        subtype='ANGLE'
    )

    axis: EnumProperty(
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", "")
        ],
        name = "Shear Axis",
        description = "Axis to Shear Along",
        default = "X"
    )


    @classmethod
    def poll(cls, context):
        return bpy.context.mode == 'EDIT_MESH'


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_popup(self, event)

    def draw(self, context):
        layout = self.layout
        root = layout.column(align=True)

        prop = root.prop(self, "angle")
        prop = root.prop(self, "axis")


    def execute(self, context):
        bpy.ops.transform.shear(
            value=1/math.tan(math.radians(90) - self.angle),
            orient_axis= self.axis,
            orient_axis_ortho='X'

        )


        return {'FINISHED'}

OUT = [
    WLT_OT_AngleShear,
    WLT_OT_QuickSymmetry,
    WLT_OT_LinearizeWeights
]