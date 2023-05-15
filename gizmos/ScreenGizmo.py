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
import bgl
import blf
import math
from bl_ui.space_toolsystem_toolbar import (
    VIEW3D_PT_tools_active as view3d_tools
)


def text_init(loc, text):
    handle = bpy.types.SpaceView3D.draw_handler_add(
        draw_callback_px, (None, None, loc, text), 'WINDOW', 'POST_PIXEL'
    )
    return handle


def draw_callback_px(self, context, position, text):
    font_id = 0
    blf.enable(font_id, blf.SHADOW)
    blf.position(font_id, position[0], position[1], 0)
    blf.size(font_id, 15, 72)
    blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
    blf.draw(font_id, text)


def active_tool():
    return view3d_tools.tool_active_from_context(bpy.context)


def get_tools():
    return view3d_tools.tools_from_context(bpy.context)

def get_region_center(context):
    center = (35, 35)

    window_size = (800, 600)
    tb_width = 0

    for region in context.area.regions:
        if region.type == 'WINDOW':
            center = (region.width/2, region.height/2)
            window_size = (region.width, region.height)
        if region.type == 'TOOLS':
            tb_width = region.width

    center = ((window_size[0] - tb_width)/2, (window_size[1]/2))
    return center


def get_toolbar_offset(context):
    offset = 0

    for region in context.area.regions:
        if region.type == 'TOOLS':
            if region.width > 1:
                offset = region.width

    return offset


class WLT_FlatGizmo(bpy.types.GizmoGroup):
    bl_idname = "WLT_screen_gizmo"
    bl_label = "WLT Screen Gizmo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'SHOW_MODAL_ALL', 'SCALE', 'VR_REDRAWS'}

    labels = (
        "Bevel",
        "Solidify",
        "Mirror",
        "Screw",
        "Simple Deform",
        "Array"
    )

    @classmethod
    def poll(cls, context):
        return True

    def setup(self, context):
        self.buttons = []
        self.handler = None
        self.show_label = False
        buttons = self.buttons

        self.center = get_region_center(context)

        self.motion_state = 0.0
        self.shift_factor = 0.0
        self.animating = True

        icons = (
            'MOD_BEVEL',
            'MOD_SOLIDIFY',
            'MOD_MIRROR',
            'MOD_SCREW',
            'MOD_SIMPLEDEFORM',
            'MOD_ARRAY',
        )

        ops = (
            'BEVEL',
            'SOLIDIFY',
            'MIRROR',
            'SCREW',
            'SIMPLE_DEFORM',
            'ARRAY'
        )

        for i in range(6):
            buttons.append(self.gizmos.new('GIZMO_GT_button_2d'))
            buttons[i].draw_options = {'OUTLINE', 'BACKDROP'}
            buttons[i].icon = icons[i]
            op = buttons[i].target_set_operator("object.modifier_add")
            op.type = ops[i]

            buttons[i].matrix_basis[0][3] = -60
            buttons[i].matrix_basis[1][3] = self.center[1] * 2 - 120 - (i * 50)

            buttons[i].color = 0.25, 0.25, 0.25
            buttons[i].alpha = 0.0

            buttons[i].color_highlight = 1.0, 0.5, 0.5
            buttons[i].alpha_highlight = 0.25

            buttons[i].scale_basis = 15


    def draw_prepare(self, context):
        buttons = self.buttons
        self.center = get_region_center(context)
        t = self.motion_state
        offset = get_toolbar_offset(context)
        labels = self.labels

        label_index = -1

        if self.animating:
            if not math.isclose(self.motion_state, 1.0, rel_tol=0.01, abs_tol=0.005):
                self.shift_factor = (t * t * ( 3.0 - 2.0 * t))
                self.motion_state += 0.02
            else: 
                self.animating = False

        for i, button in enumerate(buttons):

            if self.animating:
                button.matrix_basis[0][3] = -40 + (self.shift_factor * (75 - offset))
                if not button.alpha == 1:
                    button.alpha = (self.shift_factor * self.shift_factor) * 0.25
            else:
                button.matrix_basis[0][3] = 35 + offset
 
            button_y = self.center[1] * 2 - 120 - (i * 50)
            button.matrix_basis[1][3] = button_y

            button_loc = (button.matrix_basis[0][3], self.center[1])
            button_loc = (500, 500)

            if button.is_highlight:
                label_index = i

        if not label_index == -1:
            if not self.show_label:
                button_loc = (buttons[i].matrix_basis[0][3] + 20, (self.center[1] * 2 - 120 - (label_index * 50) - 6))
                self.handler = text_init(button_loc, labels[label_index])
                self.show_label = True
        else:
            if self.show_label:
                bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
                self.show_label = False



        # for i in range(6):
        #     if self.animating:
        #         buttons[i].matrix_basis[0][3] = -40 + (self.shift_factor * (75 - offset))
        #         if not buttons[i].alpha == 1.25:
        #             x = buttons[i].alpha
        #             buttons[i].alpha = (self.shift_factor * self.shift_factor) * 0.125
        #     else:
        #         buttons[i].matrix_basis[0][3] = 35 + offset
 
        #     buttons[i].matrix_basis[1][3] = self.center[1] * 2 - 120 - (i * 50)

        if context.gizmo_group:
            print("There's a group!")

