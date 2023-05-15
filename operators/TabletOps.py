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
from bpy.props import (
    StringProperty,
    # EnumProperty,
    # IntProperty
)
from mathutils import Matrix, Vector, Quaternion
import math
import msvcrt
import time
import datetime
import winsound
import ast

from ..utilities.DeepInspect import (
    isModalRunning
)

from ..utilities.Draw import make_batch_edges
from ..utilities.Draw import draw_batch

from ..singletons import RM as rhythm_manager


class WLT_OT_SuperTabletPie(bpy.types.Operator):
    """A pie menu for tablet users, wrapped in an operator so we can do input event processing"""
    bl_idname = "wlt.super_tablet_pie"
    bl_label = "WLT Super Tablet Pie"
    bl_description = """Fancy Things"""
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        val = isModalRunning()
        return not val


    def execute(self, context):
        print("FIN")
        return {'FINISHED'}


    def modal(self, context, event):
        context.area.header_text_set("In WLT Tablet Modal")

        if event.type in {'MOUSEMOVE', 'MIDDLEMOUSE'}:
            dist = abs(self.m_loc[0] - event.mouse_region_x) + abs(self.m_loc[1] - event.mouse_region_y)

            if dist > 50:
                self.lclick_down = False
                self.lclick_time = 0.0
                self.lclick_long = False
            return {'PASS_THROUGH'}

        if event.type == 'SPACE':
            if (event.value == 'PRESS') and (event.is_repeat == False):
                self.spacemod = True
            elif event.value == 'RELEASE':
                self.spacemod = False

        if event.type == 'SPACE':
            giz = context.gizmo_group
            print(str(giz))

        if event.type == 'LEFTMOUSE':
            if (event.value == 'CLICK_DRAG') and (event.pressure < 0.2):
                bpy.ops.transform.translate('INVOKE_DEFAULT', True, cursor_transform=True)
                return {'RUNNING_MODAL'}

            if (event.value == 'PRESS') and (event.is_repeat == False):

                self.m_loc = (event.mouse_region_x, event.mouse_region_y)

                self.lclick_time = time.time()
                self.lclick_down = True
                self.armed = True

                return {'PASS_THROUGH'}

            if event.value == 'CLICK':
                t = time.time() - self.lclick_time

                if (t > 0.75) and (t < 5.75) and (self.armed):

                    self.lclick_down = False
                    self.lclick_long = False

                    bpy.ops.mesh.loop_select('INVOKE_DEFAULT', True, extend=True, deselect=False, toggle=False, ring=False)

                    self.lclick_time = time.time()
                    self.armed = False
                    return {'RUNNING_MODAL'}

                self.lclick_down = False
                self.lclick_time = 0.0
                self.lclick_long = False
            return {'PASS_THROUGH'}

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            if event.value == 'CLICK':

                context.area.header_text_set(None)
                bpy.context.workspace.WLT.modal_state.tablet_modal = False
                bpy.context.window_manager.gizmo_group_type_unlink_delayed("WLT_TG_GG")

                return {'CANCELLED'}
            else:
                return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        m_x = event.mouse_region_x
        m_y = event.mouse_region_y
        m_loc = (m_x, m_y)

        self.m_loc = m_loc
        self.victim = -1
        self.face_2d_sel = (0, 0)

        context.area.header_text_set("In WLT Tablet Modal")

        bpy.context.workspace.WLT.modal_state.tablet_modal = True
        bpy.context.window_manager.gizmo_group_type_ensure("WLT_TG_GG")

        self.tablet = False

        self.spacemod = False

        self.lclick_down = False
        self.lclick_time = 0.0
        self.lclick_long = False

        self.armed = True

        if event.is_tablet:
            self.tablet = True

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def recursive_invoke():
    bpy.ops.wlt.tap_it('INVOKE_DEFAULT', False, mode="CHECK")


class WLT_OT_RhythmInvoke(bpy.types.Operator):
    bl_idname = "wlt.tap_it"
    bl_label = "WLT TAP"
    bl_description = """Fancy Things"""
    # bl_options = {'REGISTER'}

    mode: StringProperty(
        name="Exec Mode",
        default="INPUT"
    )

    def run_operator(self, op):
        """Runs the operator passed to it. Hacky as hell."""
        op_name = op.get("idname").split(".")
        op_props = op.get("properties")

        full_op = getattr(getattr(bpy.ops, op_name[0]), op_name[1])

        args = ('EXEC_DEFAULT', True)
        full_op.__call__(*args, **op_props)

    def invoke(self, context, event):

        if self.mode == "INPUT":
            rhythm_manager.add_input()

            # HACK WARNING: unregister and re-register timer to extend time.
            if bpy.app.timers.is_registered(recursive_invoke):
                bpy.app.timers.unregister(recursive_invoke)
                bpy.app.timers.register(recursive_invoke, first_interval=1.0)
            else:
                bpy.app.timers.register(recursive_invoke, first_interval=4.0)
            return {'FINISHED'}

        if self.mode == "CHECK":
            op = rhythm_manager.check_sequence()

            if not op == None:
                self.run_operator(op)

            return {'FINISHED'}


class WLT_OT_DRAW(bpy.types.Operator):
    """
    Non-functional. Made it to learn how OpenGL stuff works. 
    """
    bl_idname = "wlt.draw_it"
    bl_label = "WLT DRAW"
    bl_description = """Fancy Things"""
    # bl_options = {'REGISTER'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            self.loc = (event.mouse_region_x, event.mouse_region_y)
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._mesh_handle, 'WINDOW')
            return {'CANCELLED'}
        else:
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)

            self.loc = (event.mouse_region_x, event.mouse_region_y)
            self.offset = (20, 20)

            self.obj = bpy.context.active_object

            mesh_batch, mesh_shader = make_batch_edges(self, context)
            mesh_args = (self, context, mesh_shader, mesh_batch)
            self._mesh_handle = bpy.types.SpaceView3D.draw_handler_add(draw_batch, mesh_args, 'WINDOW', 'POST_VIEW')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

OUT = [
    WLT_OT_SuperTabletPie,
    WLT_OT_RhythmInvoke,
    WLT_OT_DRAW,
]