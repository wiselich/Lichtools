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
from bpy.props import (
    BoolProperty, IntProperty,
    FloatVectorProperty,
    EnumProperty
)
from ..utilities.Raycast import build_mouse_vec
from ..utilities.Draw import draw_modal_text_px

from ..singletons import EN as env_manager

class WLT_OT_ToolTip(bpy.types.Operator):
    """Use this operator to display inline tooltips."""
    bl_idname = "wlt.tool_tip"
    bl_label = "WLT Tool Tip"
    bl_description = "If you can read this, something is broken."

    tooltip: bpy.props.StringProperty(default="")

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip

    def execute(self, context):
        return {'CANCELLED'}


class WLT_OT_ResetPropertyGroup(bpy.types.Operator):
    """This operator is a hacky fix for a hacky fix. Use with caution"""
    bl_idname = "wlt.reset_group"
    bl_label = "WLT Reset Property Group"
    bl_description = "If you can read this, something is broken."

    def execute(self, context):
        props = context.workspace.WLT
        for item in props.keys():
            props.property_unset(item)

        return {'FINISHED'}


class WLT_OT_SelectID(bpy.types.Operator):
    """ID eyedroppers can't be used in popovers and pies. Use this instead"""
    bl_idname = "wlt.select_id"
    bl_label = "WLT Select ID"
    bl_description = "If you can read this, something is broken."

    def modal(self, context, event):
        self.loc = (event.mouse_region_x, event.mouse_region_y)
        ray_origin, ray_vec = build_mouse_vec(
                        context.region,
                        context.region_data,
                        self.loc,
                        )

        hit, hit_loc, hit_norm, hit_index, hit_obj, hit_mat = context.scene.ray_cast(
            depsgraph=context.evaluated_depsgraph_get(),
            origin=ray_origin,
            direction=ray_vec,
        )
        if hit:
            self.target = hit_obj
            self.text = self.target.name
            context.area.header_text_set(self.target.name)
        else:
            self.target = None
            self.text = ""   

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            context.area.header_text_set(None)
            return {'CANCELLED'}

        if event.type in {'LEFTMOUSE'}:
            if self.target:
                context.workspace.WLT.vp_orbit_target = self.target
                bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
                context.area.header_text_set(None)
                bpy.context.area.tag_redraw()
                return {'FINISHED'}
            else:
                bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
                context.area.header_text_set(None)
                return {'CANCELLED'}

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.target = None
        self.loc = (event.mouse_region_x, event.mouse_region_y)
        self.offset = (0,0)
        self.text = ""

        args = (self, context)
        self.handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_modal_text_px,
            args,
            'WINDOW',
            'POST_PIXEL'
        )

        context.area.header_text_set("In WLT ID Picker Modal")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class WLT_OT_PlayToFrame(bpy.types.Operator):
    """Modal Hackery. Use Cautiously"""
    bl_idname = "wlt.play_to_frame"
    bl_label = "WLT Play to Frame"
    bl_description = "If you can read this, something is broken."

    target_frame: IntProperty(
        name="Target Frame",
        default=34,
    )

    reverse: BoolProperty(
        name="Reverse",
        default=True
    )

    def modal(self, context, event):

        if context.scene.frame_current in self.marker_frames:
            if self.first:
                self.first = False
                context.scene.frame_current += self.delta
                return {'RUNNING_MODAL'}
            context.area.header_text_set(None)
            bpy.ops.screen.animation_play(
                "INVOKE_DEFAULT",
                True,
            )
            return {'FINISHED'}

        if self.first:
            if not context.scene.frame_current == self.start:
                self.first = False

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set(None)
            bpy.ops.screen.animation_play(
                "INVOKE_DEFAULT",
                True,
            )
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.marker_frames = []
        self.start = context.scene.frame_current
        if self.reverse:
            self.delta = -1
        else:
            self.delta = 1
        for marker in context.scene.timeline_markers:
            self.marker_frames.append(marker.frame)

        context.area.header_text_set("In WLT Playback Modal")
        context.window_manager.modal_handler_add(self)
        bpy.ops.screen.animation_play(
            "INVOKE_DEFAULT",
            True,
            reverse = self.reverse
        )
        self.first = True
        return {'RUNNING_MODAL'}


class WLT_OT_Generic(bpy.types.Operator):
    """ID eyedroppers can't be used in popovers and pies. Use this instead"""
    bl_idname = "wlt.generic_debug"
    bl_label = "WLT Generic Debug"
    bl_description = "If you can read this, something is broken."

    def execute(self, context):
        env_manager.ev_test_print()
        return {'FINISHED'}

OUT = [
    WLT_OT_ToolTip,
    WLT_OT_ResetPropertyGroup,
    WLT_OT_SelectID,
    WLT_OT_PlayToFrame,
    WLT_OT_Generic,
]