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

#  __  __     __   ___      __
# |__)|_  /\ |  \   | |__||(_ 
# | \ |__/--\|__/   | |  ||__)
# 
# I'm doing fucky shit here.
# You've been warned.

import bpy

from bpy.props import (
    FloatVectorProperty,
    FloatProperty,
    EnumProperty,
    BoolProperty,
    IntProperty
)
from bl_ui.space_toolsystem_toolbar import (
    VIEW3D_PT_tools_active as view3d_tools
)

class WLT_OT_SmartBrushInvert(bpy.types.Operator):
    """Wrapper for transform.rotate"""
    bl_idname = "wlt.smart_brush_invert"
    bl_label = "WLT Smart Brush Invert"
    bl_description = "Inverts you brush. But, like, in a smart way."
    bl_options = {'REGISTER'}

    mode_items = [
        ("INVERT_COLOR", "Invert Color", "", 1),
        ("INVERT_MODE", "Invert Blend Mode", "", 2),
        ("INVERT_COMBINED", "Invert Color and Blending", "", 3),
    ]

    mode: EnumProperty(
        items=mode_items,
        name="Mode",
        description="How inversion is calculated",
        default='INVERT_COMBINED'
    )

    auto_stroke: BoolProperty(
        name="Auto-Stroke",
        description="Initiate brush stroke after toggling",
        default=False
    )


    def invoke(self, context, event):
        brush = context.tool_settings.image_paint.brush
        initial_blend_mode = brush.blend
        inversion_mode = self.mode

        if inversion_mode == 'INVERT_COMBINED':
            if brush.blend in {'MUL', 'DARKEN'}:
                brush.blend = 'LIGHTEN'
            elif brush.blend in {'MIX', 'ADD'}:
                brush.blend = 'SUB'
            elif brush.blend in {'SUB'}:
                brush.blend = 'ADD'

        if self.auto_stroke:
            bpy.ops.paint.image_paint('INVOKE_DEFAULT', True)

        # brush.blend = initial_blend_mode

        return {'FINISHED'}

class WLT_OT_SmartBrushMaskManager(bpy.types.Operator):
    """Wrapper for transform.rotate"""
    bl_idname = "wlt.smart_brush_mask_manager"
    bl_label = "WLT Smart Brush Mask Manager"
    bl_description = "De-bullshits brush masks."
    bl_options = {'REGISTER'}

    mode_items = [
        ("SWAP", "Swap Mask Type", "", 1),
        ("TOGGLE", "Toggle Mask", "", 2),
        ("SMORT", "Big Brain Time", "", 3),
        ("PANEL", "Show Mask UI", "", 3),
    ]

    mode: EnumProperty(
        items=mode_items,
        name="Mode",
        description="Operator mode",
        default='TOGGLE'
    )

    toggle_items = [
        ("MASK", "Mask", "", 1),
        ("TEXTURE", "Texture", "", 2),
    ]

    toggle_target: EnumProperty(
        items=toggle_items,
        name="Toggle Target",
        description="Which mask to toggle",
        default='MASK'
    )

    def invoke(self, context, event):
        WLT_settings = context.workspace.WLT
        brush = context.tool_settings.image_paint.brush
        mode = self.mode
        has_mask = True if brush.mask_texture else False
        has_texture = True if brush.texture else False



        if mode == 'SWAP':
            if has_mask and has_texture:
                self.report({'INFO'}, "Both are Enabled")
                return {'CANCELLED'}
            elif has_mask:
                brush.texture = brush.mask_texture
                brush.mask_texture = None
            elif has_texture:
                brush.mask_texture = brush.texture
                brush.texture = None
            else:
                self.report({'INFO'}, "WLT Mask Toggle: Nothing to toggle here")
                return {'CANCELLED'}
        elif mode == 'TOGGLE':
            if self.toggle_target == 'MASK':
                if has_mask:
                    brush.wlt.mask_tex = brush.mask_texture
                    brush.mask_texture.use_fake_user = True
                    brush.mask_texture = None
                else:
                    brush.mask_texture = brush.wlt.mask_tex
            else:
                if has_texture:
                    brush.wlt.tex = brush.texture
                    brush.texture.use_fake_user = True
                    brush.texture = None
                else:
                    brush.texture = brush.wlt.tex

        return {'FINISHED'}


class WLT_PT_BrushBox(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_label = "Brush Box"
    bl_options = { 'HEADER_LAYOUT_EXPAND',  }

    def draw(self, context):
        WLT_props = context.workspace.WLT
        paint_settings = context.tool_settings.image_paint

        active_tool = view3d_tools.tool_active_from_context(bpy.context)
        tool_name = active_tool.idname[14:].upper()

        layout = self.layout
        root = layout.column(align=True)
        grid = root.grid_flow()

        for brush in bpy.data.brushes:
            if brush.use_paint_image and (brush.image_tool == tool_name):
                col = grid.column(align=True)
                icon = layout.icon(brush)
                col.template_icon(icon, scale=5.0)
                col.prop(
                    bpy.data.brushes,
                    bpy.data.brushes.path_from_id()
                )
                col.label(text=brush.name)


        # root.template_ID_preview(
        #     paint_settings,
        #     "brush",
        #     new="brush.add",
        #     rows=3,
        #     cols=8,
        #     hide_buttons=True
        #     )


class WLT_OT_BrushBox(bpy.types.Operator):
    """Wrapper for transform.rotate"""
    bl_idname = "wlt.brush_box"
    bl_label = "WLT Brush Box"
    bl_description = "Get your brushes here."
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.call_panel(name='WLT_PT_BrushBox')
        return {'FINISHED'}

OUT = [
    WLT_OT_SmartBrushInvert,
    WLT_OT_SmartBrushMaskManager,
    WLT_PT_BrushBox,
    WLT_OT_BrushBox,
]