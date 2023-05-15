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
from bpy.types import (
    KeyingSet, Panel,
    Curve,
    SurfaceCurve
)

from ..utilities.WidthFunc import (
    get_breakpoints,
    # get_width_factor,
    check_width,
    get_break_full
)

def active_tool():
    return view3d_tools.tool_active_from_context(bpy.context)


class VIEW3D_PT_anim_panel(Panel):
    bl_idname = "VIEW3D_PT_anim_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "WLT"
    bl_label = "Anim Panel"
    bl_options = { 'HEADER_LAYOUT_EXPAND',  }


    def draw(self, context):
        WLT_props = context.workspace.WLT
        scene = context.scene
        tool_settings = context.tool_settings
        keyset = scene.keying_sets.active

        layout = self.layout
        root = layout.column(align=True)

        row = root.row(align=True)
        row.prop(tool_settings, "keyframe_type", text="")
        row.operator(
            'anim.keyframe_insert',
            text='',
            icon='KEY_HLT'
        )
        row.operator(
            'anim.keyframe_delete',
            text='',
            icon='KEY_DEHLT'
        )

        row = root.row(align=True)

        col = row.column(align=True)
        col.template_list("UI_UL_list", "keying_sets", scene, "keying_sets", scene.keying_sets, "active_index", rows=1)

        col = row.column(align=True)
        col.operator("anim.keying_set_add", icon='ADD', text="")
        col.operator("anim.keying_set_remove", icon='REMOVE', text="")

        root.separator(factor=1)

        unique_ids = []
        id_dict = {}
        blank_paths = []

        if keyset:
            for path in keyset.paths:
                if not path.id:
                    blank_paths.append(path)
                    continue

                if not path.id in unique_ids:
                    unique_ids.append(path.id)
                    id_dict[path.id] = []

                id_dict[path.id].append(path)

            for datablock, paths, in id_dict.items():
                box = root.box()
                boxcol = box.column(align=True)
                label_row = boxcol.row(align=True)
                label_row.label(text=str(datablock.name), icon_value=layout.icon(datablock))
                label_row_right = label_row.row(align=True)
                label_row_right.alignment = 'RIGHT'
                label_row_right.operator("anim.keying_set_path_add", icon='ADD', text="")
                boxcol.separator(factor=1)

                for path in paths:
                    row = boxcol.row(align=True)
                    row.template_path_builder(
                        path,
                        "data_path",
                        path.id,
                        text="")
                    row.label(text="", icon='X')

            for path in blank_paths:
                box = root.box()
                boxcol = box.column(align=True)

                row = boxcol.row(align=True)
                row.use_property_split = True
                row.use_property_decorate = False
                row.template_any_ID(path, "id", "id_type", text="Target:")

                row = boxcol.row(align=True)
                row.template_path_builder(
                    path,
                    "data_path",
                    path.id,
                    text="")
                row.label(text="", icon='X')

                root.separator(factor=1)
            
            root.operator("anim.keying_set_path_add", icon='ADD', text="")

OUT = [
    VIEW3D_PT_anim_panel
]