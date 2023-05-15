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
    Panel,
)


class VIEW3D_PT_view3d_fast_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    # bl_category = "WLT"
    bl_label = "Fast Panel"
    # bl_options = {'DRAW_BOX'}

    @classmethod
    def get_shading(cls, context):
        view = context.space_data
        if view.type == 'VIEW_3D':
            return view.shading
        else:
            return context.scene.display.shading

    def draw(self, context):

        # Aliased Stuff
        scene = context.scene
        units = scene.unit_settings
        overlay = context.space_data.overlay
        view = context.space_data
        shading = VIEW3D_PT_view3d_fast_panel.get_shading(context)
        active_obj = context.active_object

        # Fast Panel Property Group
        wm = bpy.context.window_manager
        fp_props = context.workspace.WLT

        if context.active_object:
            if context.active_object.type == 'MESH':
                active_mat = context.active_object.active_material
            # active_mesh = context.active_object.data

        layout = self.layout

        # if fp.layout_bool:
        #     layout.ui_units_x = 60
        #     root = layout.grid_flow(columns=4, even_columns=True, align=False)
        # else:

        root = layout.grid_flow(columns=1, even_columns=True, align=False)
        layout.ui_units_x = 12

        root.scale_y = 1

        # TODO: Clean up naming conventions
        root_column = root.column(align=True)
        tab_row = root_column.row(align=False)
        tab_row.alignment = 'EXPAND'

        tab_row_left = tab_row.row(align=True)
        tab_row_left.alignment = 'LEFT'

        tab_row_left.operator("wlt.toggle_photo_mode", text="", icon='FULLSCREEN_ENTER')

        op = tab_row_left.operator("wm.call_panel", text="", icon='OPTIONS')
        op.name="VIEW3D_PT_meta_panel"

        no_emboss= tab_row_left.row(align=True)
        no_emboss.emboss = 'NONE'
        op = no_emboss.operator("wlt.tool_tip", text="", icon='INFO')
        op.tooltip = "This is a tooltip"

        tab_row_right = tab_row.row(align=True)
        tab_row_right.alignment = 'RIGHT'

        # tab_row.prop(fp, "layout_bool", text="", icon="KEYFRAME_HLT")
        tab_row_right.prop(fp_props, "fp_tabs", expand=True, icon_only=True)

        root_column.separator()

        # Measures Row
        if fp_props.fp_tabs == 'MEASURES':
            body = root_column.column(align=True)
            but_row = body.row(align=True)

            if (context.active_object and context.active_object.type == 'MESH'):

                r_row = body.row(align=True)
                r_col = r_row.column(align=True)
                row = r_col.row(align=True)

                row.prop_enum(
                    context.object,
                    "display_type",
                    'BOUNDS',
                    text="Box",
                )
                row.prop_enum(
                    context.object,
                    "display_type",
                    'WIRE',
                    text="Wire",
                )
                row.prop_enum(
                    context.object,
                    "display_type",
                    'TEXTURED',
                    text="Full",
                )
                row = r_col.row(align=True)

                if context.active_object:

                    if context.active_object.type == 'MESH':
                        active_mesh = context.active_object.data
                        row.prop(
                            active_mesh,
                            "use_auto_smooth",
                            text="Auto Smooth",
                            # icon='MOD_NORMALEDIT',
                            toggle=True
                        )
                        row.prop(
                            active_mesh,
                            "auto_smooth_angle",
                            text="",
                        )

                col = r_row.column(align=True)
                row = col.row(align=True)

                row.prop(
                    overlay,
                    "show_extra_edge_length",
                    text="",
                    toggle=True,
                    icon='EDGESEL'
                )
                row.prop(
                    overlay,
                    "show_extra_edge_angle",
                    text="",
                    toggle=True,
                    icon='DRIVER_ROTATIONAL_DIFFERENCE'
                )
                row.prop(
                    overlay,
                    "show_extra_face_area",
                    text="",
                    toggle=True,
                    icon='CON_SIZELIMIT'
                )
                row.prop(
                    overlay,
                    "show_extra_face_angle",
                    text="",
                    toggle=True,
                    icon='MOD_SOLIDIFY'
                )
                row.prop(
                    context.object,
                    "show_wire",
                    text="",
                    icon='MOD_WIREFRAME',
                    toggle=True
                )

                row = col.row(align=True)

                if context.active_object:
                    if context.mode == 'OBJECT' and context.active_object.type == 'MESH':
                        row.operator(
                            "object.shade_smooth",
                            text="Set Smooth",
                            # icon='NORMALS_VERTEX_FACE'
                        )
                    elif context.mode == 'OBJECT' and context.active_object.type == 'CURVE':
                        row.operator(
                            "curve.shade_smooth"
                        )
                    elif context.mode == 'EDIT_MESH':
                        row.operator(
                            "mesh.faces_shade_smooth",
                        )
            body.separator()
            statvis = context.scene.tool_settings.statvis
            statvis_col = body.column(align=True)
            subrow = statvis_col.row(align=True)
            subrow.prop(
                    overlay,
                    "show_statvis",
                    text="Mesh Viz",
                    toggle=True
            )
            subrow.prop(statvis, "type", text="")

            subrow = statvis_col.row(align=True)
            subrow.active = (True if overlay.show_statvis else False)

            if statvis.type == 'OVERHANG':
                subrow.prop(statvis, "overhang_min", text="Min")
                subrow.prop(statvis, "overhang_max", text="Max")
                subrow.prop(statvis, "overhang_axis", text="")
            if statvis.type == 'THICKNESS':
                subrow.prop(statvis, "thickness_min", text="Min")
                subrow.prop(statvis, "thickness_max", text="Max")
                subrow.prop(statvis, "thickness_samples", text="")
            if statvis.type == 'DISTORT':
                subrow.prop(statvis, "distort_min", text="Min")
                subrow.prop(statvis, "distort_max", text="Max")
            if statvis.type == 'SHARP':
                subrow.prop(statvis, "sharp_min", text="Min")
                subrow.prop(statvis, "sharp_max", text="Max")

            body.separator()
            split = body.split(factor=0.645, align=True)

            col = split.column(align=True)
            col.prop(overlay, "grid_scale", text="Grid Scale")
            row = col.row(align=True)

            row.prop(overlay, "show_axis_x", text="X", toggle=True)
            row.prop(overlay, "show_axis_y", text="Y", toggle=True)
            row.prop(overlay, "show_axis_z", text="Z", toggle=True)
            row.prop(overlay, "show_floor", text="Floor", toggle=True)
            row.prop(overlay, "show_ortho_grid", text="Ortho", toggle=True)

            col = split.column(align=True)
            col.prop(units, "system", text="")
            col.prop(units, "length_unit", text="")

            ###

            body.separator()
            tog_row = body.row(align=True)
            if shading.type == 'SOLID':
                tog_row.prop(shading, "xray_alpha", text="X-Ray")
            elif shading.type == 'WIREFRAME':
                tog_row.prop(shading, "xray_alpha_wireframe", text="X-Ray")
            tog_row.prop(overlay, "backwire_opacity", text="Wires")
            tog_row.prop(
                    shading,
                    "show_xray",
                    text="",
                    icon='XRAY',
                    toggle=True,
                    invert_checkbox=False
            )

            shading_root = body.row(align=True)

            if not shading.type == 'WIREFRAME':
                shading_root.template_icon_view(
                    shading,
                    "studio_light",
                    scale=2,
                    scale_popup=2.0
                )

            if shading.type == 'SOLID':
                shading_row = shading_root.split(factor=0.9, align=True)
                col = shading_row.row(align=True)

                subcol = col.column(align=True)
                subcol.prop_enum(
                    shading,
                    "color_type",
                    'MATERIAL'
                )
                subcol.prop_enum(
                    shading,
                    "color_type",
                    'VERTEX'
                )

                subcol = col.column(align=True)
                subcol.prop_enum(
                    shading,
                    "color_type",
                    'SINGLE'
                )
                subcol.prop_enum(
                    shading,
                    "color_type",
                    'TEXTURE'
                )

                subcol = col.column(align=True)
                subcol.prop_enum(
                    shading,
                    "color_type",
                    'OBJECT'
                )
                subcol.prop_enum(
                    shading,
                    "color_type",
                    'RANDOM'
                )
            elif shading.type == 'WIREFRAME':
                shading_row = shading_root.column(align=True)
                col = shading_row.row(align=True)

                subcol = col.column(align=True)
                subcol.prop_enum(
                    shading,
                    "wireframe_color_type",
                    'SINGLE'
                )

                subcol = col.column(align=True)
                subcol.prop_enum(
                    shading,
                    "wireframe_color_type",
                    'OBJECT'
                )

                subcol = col.column(align=True)
                subcol.prop_enum(
                    shading,
                    "wireframe_color_type",
                    'RANDOM'
                )
            elif shading.type == 'MATERIAL':
                shading_row = shading_root.row(align=True)
                col = shading_row.row(align=True)

                subcol = col.column(align=True)

                subrow = subcol.row(align=True)
                subrow.prop(
                    shading,
                    "studiolight_rotate_z",
                    text="Angle"
                )
                subrow.prop(
                    shading,
                    "studiolight_background_alpha",
                    text="Alpha"
                )
                subcol.prop(
                    shading,
                    "studiolight_intensity",
                )
            else:
                shading_row = shading_root.split(factor=0.9, align=True)

            col = shading_row.column(align=True)
            col.scale_y = 2
            if active_obj:
                if (shading.color_type == 'SINGLE' and (shading.type == 'SOLID'
                                                        or shading.type == 'WIREFRAME')):
                    if shading.type == 'WIREFRAME':
                        col.scale_y = 1
                    col.prop(shading, "single_color", text="")
                elif (shading.color_type == 'OBJECT' and active_obj.type == 'MESH'
                        and (shading.type == 'SOLID' or shading.type == 'WIREFRAME')):
                    if shading.type == 'WIREFRAME':
                        col.scale_y = 1
                    col.prop(active_obj, "color", text="")

        # $Second Tab
        if fp_props.fp_tabs == 'OVERLAYS':
            body = root_column.column()
            body = body.column(align=True)
            but_row = body.row(align=True)

            # $Normals
            but_row.prop(overlay, "normals_length", text="Normals")
            but_row.prop(
                overlay,
                "show_vertex_normals",
                text="",
                icon='NORMALS_VERTEX'
            )
            but_row.prop(
                overlay,
                "show_split_normals",
                text="",
                icon='NORMALS_VERTEX_FACE'
            )
            but_row.prop(
                overlay,
                "show_face_normals",
                text="",
                icon='NORMALS_FACE'
            )
            but_row.prop(
                overlay,
                "show_face_orientation",
                text="",
                toggle=True,
                invert_checkbox=False,
                icon='ORIENTATION_LOCAL'
            )

            but_row = body.row(align=True)
            but_row.prop(
                shading,
                "show_backface_culling",
                text="Cull Backfaces",
                toggle=True,
                invert_checkbox=False,
            )
            but_row.prop(
                overlay,
                "show_face_orientation",
                text="Orientation",
                toggle=True,
                invert_checkbox=False,
            )
            if context.active_object:
                if context.mode == 'OBJECT' and context.active_object.type == 'MESH':
                    but_row.operator(
                        "object.shade_smooth"
                    )
                elif context.mode == 'OBJECT' and context.active_object.type == 'CURVE':
                    but_row.operator(
                        "curve.shade_smooth"
                    )
                elif context.mode == 'EDIT_MESH':
                    but_row.operator(
                        "mesh.faces_shade_smooth"
                    )
                if context.active_object.type == 'MESH':
                    active_mesh = context.active_object.data
                    but_row.prop(
                        active_mesh,
                        "use_auto_smooth",
                        text="",
                        icon='MOD_NORMALEDIT',
                        toggle=True
                    )

            # $MeshOverlays
            body.separator()
            but_row = body.row(align=True)

            but_row.prop(
                overlay,
                "show_edge_crease",
                text="Crease",
                toggle=True,
                icon='MOD_SUBSURF'
            )
            but_row.prop(
                overlay,
                "show_edge_sharp",
                text="Sharp",
                toggle=True,
                icon='MOD_EDGESPLIT'
            )
            but_row.prop(
                overlay,
                "show_edge_bevel_weight",
                text="Bevel",
                toggle=True,
                icon='MOD_BEVEL'
            )
            but_row.prop(
                overlay,
                "show_edge_seams",
                text="Seam",
                toggle=True,
                icon='UV_DATA'
            )

            but_row = body.row(align=True)

            but_row.prop(
                overlay,
                "show_edges",
                text="Edges",
                toggle=True,
                icon='MOD_WIREFRAME'
            )
            but_row.prop(
                overlay,
                "show_faces",
                text="Faces",
                toggle=True,
                icon='FACE_MAPS'
            )
            but_row.prop(
                overlay,
                "show_face_center",
                text="Face Dots",
                toggle=True,
                icon='SNAP_FACE_CENTER'
            )

        # Display Row
            body.separator()
            but_row = body.row(align=True)

            if (context.active_object and context.active_object.type == 'MESH'):
                but_row.prop(context.object, 'display_type', expand=True)

                but_row = body.split(factor=0.65, align=True)

                but_row_left = but_row.row(align=True)
                # but_row_left.scale_x = 0.5
                but_row_left.prop(
                    context.object,
                    'show_name',
                    text="Name",
                    toggle=True
                )
                but_row_left.prop(
                    context.object,
                    "show_wire",
                    text="Wires",
                    toggle=True
                )
                but_row_left.prop(
                    context.object,
                    "show_in_front",
                    text="Clip",
                    toggle=True,
                    invert_checkbox=True
                )
                but_row_left.prop(
                    context.object,
                    "show_axis",
                    text="Axis",
                    toggle=True
                )
                but_row_right = but_row.row(align=True)
                # but_row_right.separator(factor=1.5)
                but_row_right_inner = but_row_right.row(align=True)
                but_row_right_inner.scale_x = 1
                but_row_right_inner.prop(
                    context.object,
                    'display_bounds_type',
                    text="",
                )
                but_row_right_inner.prop(
                    context.object,
                    'show_bounds',
                    text="",
                    toggle=True,
                    icon='PIVOT_BOUNDBOX'
                )

            elif (active_obj and active_obj.type == 'EMPTY'):
                but_row.prop(
                    context.object,
                    'empty_display_type',
                    text="",
                    expand=False
                )
                but_row.prop(
                    context.object,
                    'parent',
                    text="",
                )

                but_row_split = body.split(factor=0.5, align=True)

                but_row_split.prop(
                    context.object,
                    'empty_display_size',
                    text="",
                    expand=False
                )

                but_row_inner = but_row_split.row(align=True)

                but_row_inner.prop(
                    context.object,
                    'show_name',
                    text="Name",
                    toggle=True
                )
                but_row_inner.prop(
                    context.object,
                    'show_axis',
                    text="Axis",
                    toggle=True
                )

            elif (active_obj and active_obj.type == 'CAMERA'):
                but_row.prop(
                    context.object.data,
                    'show_limits',
                    text="Limits",
                    toggle=True
                )
                but_row.prop(
                    context.object.data,
                    'show_mist',
                    text="Mist",
                    toggle=True
                )
                but_row.prop(
                    context.object.data,
                    'show_sensor',
                    text="Sensor",
                    toggle=True
                )
                but_row.prop(
                    context.object.data,
                    'show_name',
                    text="Name",
                    toggle=True
                )

                but_row = body.row(align=True)
                but_row.prop(
                    context.object.data,
                    'display_size',
                    text="Size",
                )


            # $Gizmos
            body.separator()
            but_row = body.row(align=True)

            but_row.prop(scene.transform_orientation_slots[1], "type", text="")
            but_row.prop(
                view,
                "show_gizmo_object_translate",
                text="",
                toggle=True,
                icon='ORIENTATION_VIEW'
                )
            but_row.prop(
                view,
                "show_gizmo_object_rotate",
                text="",
                toggle=True,
                icon='DRIVER_ROTATIONAL_DIFFERENCE'
            )
            but_row.prop(
                view,
                "show_gizmo_object_scale",
                text="",
                toggle=True,
                icon='CON_SIZELIMIT'
            )

            but_row = body.row(align=True)
            but_row.prop(
                context.preferences.view,
                "gizmo_size",
                text="Gizmo Size"
            )
            but_row.prop(
                view,
                "show_gizmo_empty_image",
                text="",
                toggle=True,
                icon='IMAGE_PLANE',
            )
            but_row.prop(
                view,
                "show_gizmo_empty_force_field",
                text="",
                toggle=True,
                icon='FORCE_VORTEX',
            )
            but_row.prop(
                view,
                "show_gizmo_light_size",
                text="",
                toggle=True,
                icon='OUTLINER_OB_LIGHT',
            )
            but_row.prop(
                view,
                "show_gizmo_light_look_at",
                text="",
                toggle=True,
                icon='LIGHT_SPOT',
            )
            but_row.prop(
                view,
                "show_gizmo_camera_lens",
                text="",
                toggle=True,
                icon='CON_CAMERASOLVER',
            )
            but_row.prop(
                view,
                "show_gizmo_camera_dof_distance",
                text="",
                toggle=True,
                icon='CAMERA_DATA',
            )
            but_row.prop(
                view,
                "show_gizmo",
                text="",
                toggle=True,
                icon='GIZMO',
            )

        # $Third Tab
        if fp_props.fp_tabs == 'NORMALS':
            tool_settings = context.scene.tool_settings

            body = root_column.column()
            
            top = body.column(align=True)
            row = top.row(align=True)

            row.prop(
                scene.transform_orientation_slots[0],
                "type",
                text="",
                icon_only=False,
                expand=False
            )
            row.prop(
                tool_settings,
                "transform_pivot_point",
                text="",
                icon_only=True,
                expand=False
            )


            snap_items = bpy.types.ToolSettings.bl_rna.properties["snap_elements"].enum_items
            snap_elements = tool_settings.snap_elements
            if len(snap_elements) == 1:
                text = " "
                for elem in snap_elements:
                    icon = snap_items[elem].icon
                    text = snap_items[elem].name
                    break
            else:
                text = "Mix"
                icon = 'NONE'
            del snap_items, snap_elements

            row.popover(
                'VIEW3D_PT_snapping',
                text=text,
                icon=icon
            )

            row.prop(
                tool_settings,
                "use_snap",
                text="",
                icon_only=True,
                expand=False
            )

            row = top.row(align=True)
            row.prop(
                tool_settings,
                "use_transform_data_origin",
                text="Origins",
                icon='TRANSFORM_ORIGINS',
                toggle=True
            )
            row.prop(
                tool_settings,
                "use_transform_pivot_point_align",
                text="Locations",
                icon='CON_PIVOT',
                toggle=True
            )
            row.prop(
                tool_settings,
                "use_transform_skip_children",
                text="Parent Only",
                icon='CON_CHILDOF',
                toggle=True
            )

            columns = body.split(factor=0.33, align=False)
            left_col = columns.column(align=True)
            left_col.alignment = 'EXPAND'
            right_col = columns.column(align=True)

            ### Left Column

            left_col.label(text="Cursor To:")
            lc_inner = left_col.grid_flow(columns=1, align=True)
            lc_inner.scale_y = 0.85

            op = lc_inner.operator(
                "wlt.align_cursor_to_orientation",
                text="Orientation"
            )

            op = lc_inner.operator(
                "wlt.smart_orient",
                text="Selected"
            )
            op.modal = True

            op = lc_inner.operator(
                "view3d.snap_cursor_to_center",
                text="Center"
            )

            ### Right Column

            right_col.label(text="Origin To:")

            grid = right_col.grid_flow(columns=2, row_major=True, align=True, even_columns=True, even_rows=False)
            grid.scale_y = 0.85

            op = grid.operator(
                "wlt.origin_to_bbox",
                text='Front Left',
            )
            op.box_mode = 'POINT'
            op.box_point = 'XNEG_YPOS_ZNEG'

            op = grid.operator(
                "wlt.origin_to_bbox",
                text='Front Right',
            )
            op.box_mode = 'POINT'
            op.box_point = 'XPOS_YPOS_ZNEG'

            op = grid.operator(
                "wlt.origin_to_bbox",
                text='Back Left',
            )
            op.box_mode = 'POINT'
            op.box_point = 'XNEG_YNEG_ZNEG'

            op = grid.operator(
                "wlt.origin_to_bbox",
                text='Back Right',
            )
            op.box_mode = 'POINT'
            op.box_point = 'XPOS_YNEG_ZNEG'

            op = grid.operator(
                "wlt.origin_to_bbox",
                text='Bottom',
            )
            op.box_mode = 'FACE'
            op.box_face = 'ZNEG'

            op = grid.operator(
                "wlt.origin_to_bbox",
                text='Center',
            )
            op.box_mode = 'FACE'
            op.box_face = 'CENTER'

            right_col.separator()
            grid = right_col.grid_flow(columns=2, row_major=True, align=True, even_columns=True, even_rows=False)
            grid.scale_y = 0.85

            op = grid.operator(
                "wlt.set_origin",
                text='Selected',
            )
            op.snap_mode = 'SELECTION'

            op = grid.operator(
                "wlt.set_origin",
                text='Cursor',
            )
            op.snap_mode = 'CURSOR'

            op = grid.operator(
                "wlt.quick_snap_origin",
                text='Modal',
            )



class VIEW3D_PT_grid_ribbon(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_label = "Grid Ribbon"
    text = "Bacon"

    @classmethod
    def get_shading(cls, context):
        view = context.space_data
        if view.type == 'VIEW_3D':
            return view.shading
        else:
            return context.scene.display.shading

    def draw(self, context):

        area = bpy.context.area
        resolution = bpy.context.preferences.system.ui_scale
        resolution_label = str(resolution)

        region_width_raw = 200

        for reg in area.regions:
            if reg.type == 'UI':
                region_width_raw = reg.width

        region_width = region_width_raw - 40
        region_width_label = str(region_width)

        region_width_int = round(region_width / (20 * resolution))
        region_width_int_label = str(region_width_int)

        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

        # region_width_factor = round((region_width / 440), 3)
        # region_width_factor_label = str(region_width_factor)

        layout = self.layout
        # layout.ui_units_x = region_width_int
        layout.scale_y = 0.85

        root = layout.column(align=True)

        break_info = root.row(align=True)

        break_info.label(text=region_width_label)
        break_info.label(text=region_width_int_label)
        break_info.label(text=resolution_label)

        col_set_1 = 0
        col_set_2 = 0
        col_set_3 = 0
        col_set_4 = 0

        if region_width_int >= 12:
            col_set_1 = 2
            col_set_2 = 4
            col_set_3 = 2
            col_set_4 = 3

        if region_width_int < 12:
            col_set_1 = 1
            col_set_2 = 2
            col_set_3 = 2
            col_set_4 = 3

        if region_width_int <= 8:
            col_set_1 = 1
            col_set_2 = 2
            col_set_3 = 2
            col_set_4 = 3

        if region_width_int <= 6:
            col_set_1 = 1
            col_set_2 = 1
            col_set_3 = 2
            col_set_4 = 3

        if region_width_int < 6:
            col_set_1 = 1
            col_set_2 = 1
            col_set_3 = 1
            col_set_4 = 3

        # Aliased Stuff
        scene = context.scene
        units = scene.unit_settings
        overlay = context.space_data.overlay

        grid_box = root.box()

        grid_box_inner_col = grid_box.column(align=False)

        row_1 = grid_box_inner_col.grid_flow(columns=col_set_1, align=True)

        row_1.prop(overlay, "grid_scale", text="Grid Scale")

        row_1_sub = row_1.grid_flow(columns=col_set_3, align=True)

        row_1_sub_left = row_1_sub.row(align=True)
        row_1_sub_left.prop(overlay, "show_floor", text="Floor", toggle=True)

        row_1_sub_right = row_1_sub.grid_flow(columns=col_set_4, align=True)
        row_1_sub_right.prop(overlay, "show_axis_x", text="X", toggle=True)
        row_1_sub_right.prop(overlay, "show_axis_y", text="Y", toggle=True)
        row_1_sub_right.prop(overlay, "show_axis_z", text="Z", toggle=True)

        row_2 = grid_box_inner_col.grid_flow(columns=col_set_2, align=True)

        row_2.prop(overlay, "grid_subdivisions", text="Subdivisions")
        row_2.prop(units, "scale_length", text="Unit Scale")
        row_2.prop(overlay, "show_ortho_grid", text="Ortho", toggle=True)
        row_2.prop(units, "length_unit", text="")

OUT = [VIEW3D_PT_view3d_fast_panel]