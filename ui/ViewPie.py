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
    Menu,
    Panel
)

class VIEW3D_MT_WLT_orbit_pie(Menu):
    bl_label = "WLT Orbit Pie"

    def draw(self, context):
        region = context.region_data
        layout = self.layout
        # view = context.space_data
        pie = layout.menu_pie()

        # LEFT
        orbit_center_label = "Enable Orbit Selected"
        if context.preferences.inputs.use_rotate_around_active:
            orbit_center_label = "Disable Orbit Selected"

        col = pie.row(align=True)
        col.emboss = 'NORMAL'
        col.alignment = 'LEFT'
        col.use_property_split = True
        col.scale_y = 1.5

        op = col.operator("wm.context_toggle", text=orbit_center_label)
        op.data_path = "preferences.inputs.use_rotate_around_active"

        # RIGHT
        orbit_mode_label = "Use Trackball Rotation"
        if context.preferences.inputs.view_rotate_method == 'TRACKBALL':
            orbit_mode_label = "Use Turntable Rotation "

        col = pie.row(align=True)
        col.emboss = 'NORMAL'
        col.alignment = 'LEFT'
        col.use_property_split = True
        col.scale_y = 1.5

        op = col.operator("wm.context_cycle_enum", text=orbit_mode_label)
        op.data_path = "preferences.inputs.view_rotate_method"
        op.wrap = True

        # if context.preferences.inputs.view_rotate_method == 'TRACKBALL':
        #     col.prop(context.preferences.inputs, "view_rotate_sensitivity_trackball")
        # else:
        #     col.prop(context.preferences.inputs, "view_rotate_sensitivity_turntable")

        op = col.operator("wm.call_panel", text="", icon='TRIA_DOWN')
        op.name = "VIEW3D_PT_viewport_rotation_panel"
        op.keep_open = True

        # BOTTOM
        persp_label = "Persp/Ortho | Manual Persp"
        persp_icon = 'VIEW_ORTHO'

        if context.preferences.inputs.use_auto_perspective:
            persp_label = "Persp/Ortho | Auto Persp"
            persp_icon = 'FORCE_CURVE'
        elif region.view_perspective == 'PERSP':
            persp_icon = 'VIEW_PERSPECTIVE'
        elif region.view_perspective == 'ORTHO':
            persp_icon = 'VIEW_ORTHO'

        context_op = pie.operator(
            "wlt.context_op",
            text=persp_label,
            icon=persp_icon
        )
        context_op.def_op = "view3d.view_persportho"
        context_op.def_op_props = ""

        context_op.ctrl_op = "wm.context_toggle"
        context_op.ctrl_op_props = "{'data_path': 'preferences.inputs.use_auto_perspective'}"

        context_op.shift_op = "wlt.set_axis"
        context_op.shift_op_props = ""

        # TOP
        col = pie.column(align=True)
        col.prop(
            context.workspace.WLT,
            'vp_orbit_target',
            text=""
        )
        row = col.row(align=True)
        op = row.operator(
            "wlt.select_id",
            text="Set Target",
            icon='EYEDROPPER'
        )
        row.prop(
            context.workspace.WLT,
            'vp_use_global_target',
            text="Use Target"
        )
        # TOP LEFT
        # TOP RIGHT

        # BOTTOM LEFT
        # BOTTOM RIGHT



class VIEW3D_MT_WLT_view_pie(Menu):
    bl_label = "WLT View Pie"

    def draw(self, context):
        region = context.region_data
        layout = self.layout
        # view = context.space_data
        pie = layout.menu_pie()

        # LEFT
        op = pie.operator("wlt.view_axis", text="Front/Back | Y Axis")
        op.axis = 'FRONT'
        op.speed = context.preferences.view.smooth_view

        # RIGHT
        op = pie.operator("wlt.view_axis", text="Right/Left | X Axis")
        op.axis = 'RIGHT'
        op.speed = context.preferences.view.smooth_view

        # BOTTOM
        op = pie.operator("wlt.view_axis", text="Top/Bottom | Z Axis")
        op.axis = 'TOP'
        op.speed = context.preferences.view.smooth_view

        # TOP
        show_cam = False
        if show_cam:
            cam_icon = 'CAMERA_DATA'
            if region.view_perspective == 'CAMERA':
                cam_icon = 'OUTLINER_OB_CAMERA'

            if context.space_data.lock_camera:
                cam_icon = 'CON_CAMERASOLVER'

            context_op = pie.operator(
                "wlt.context_op",
                text="Camera",
                icon=cam_icon
            )

            if not region.view_perspective == 'CAMERA':

                if not context.scene.camera:
                    if context.mode == 'OBJECT':
                        context_op.def_op = "object.camera_add"
                        context_op.def_op_args = "'INVOKE_DEFAULT', True,"
                        context_op.def_op_props = (
                                                "{"
                                                "'enter_editmode': False, "
                                                "'align': 'VIEW'"
                                                "}"
                                                )
                    else:
                        context_op.def_op = "object.editmode_toggle"
                        context_op.def_op_args = "'INVOKE_DEFAULT', True,"
                        context_op.def_op_props = ""
                else:
                    context_op.def_op = "view3d.view_camera"
                    context_op.def_op_args = "'INVOKE_DEFAULT', True,"
                    context_op.def_op_props = ""

                    context_op.ctrl_op = "view3d.camera_to_view"
                    context_op.ctrl_op_args = "'INVOKE_DEFAULT', True,"
                    context_op.ctrl_op_props = ""

                    context_op.shift_op = "object.select_camera"
                    context_op.shift_op_args = "'INVOKE_DEFAULT', True,"
                    context_op.shift_op_props = ""

            if region.view_perspective == 'CAMERA':
                context_op.def_op = "wm.context_toggle"
                context_op.def_op_args = "'INVOKE_DEFAULT', True,"
                context_op.def_op_props = "{'data_path': 'space_data.lock_camera'}"

                if context.active_object and context.active_object.type == 'CAMERA':
                    context_op.shift_op = "wm.context_toggle"
                    context_op.shift_op_args = "'INVOKE_DEFAULT', True,"
                    context_op.shift_op_props = "{'data_path': 'object.data.show_name'}"

                    # Toggle Ortho/Perspective Lens
                    context_op.alt_op = "wm.context_cycle_enum"
                    context_op.alt_op_args = "'INVOKE_DEFAULT', True,"
                    context_op.alt_op_props = "{'data_path': 'object.data.type', 'wrap': True}"

                    context_op.ctrl_shift_op = "wm.context_toggle"
                    context_op.ctrl_shift_op_args = "'INVOKE_DEFAULT', True,"
                    context_op.ctrl_shift_op_props = (
                                                    "{"
                                                    "'data_path': "
                                                    "'object.data.show_composition_thirds',"
                                                    "}"
                                                    )
                else:
                    context_op.ctrl_op = "view3d.view_center_camera"
                    context_op.ctrl_op_props = ""

                    context_op.shift_op = "view3d.camera_to_view_selected"
                    context_op.shift_op_props = ""

                    context_op.alt_op = "object.select_camera"
                    context_op.alt_op_props = ""
        else:
            context_op = pie.operator(
                "wlt.context_op",
                text="Settings | Camera Pie | Quad View",
            )
            context_op.def_op = "wm.call_menu_pie"
            context_op.def_op_args = "'INVOKE_DEFAULT', True,"
            context_op.def_op_props = "{'name': 'VIEW3D_MT_WLT_orbit_pie'}"

            context_op.ctrl_op = "wm.call_menu_pie"
            context_op.ctrl_op_args = "'INVOKE_DEFAULT', True,"
            context_op.ctrl_op_props = "{'name': 'VIEW3D_MT_WLT_camera_pie'}"

            context_op.shift_op = "screen.region_quadview"
            context_op.shift_op_args = "'INVOKE_DEFAULT', True,"
            context_op.shift_op_props = ""

        # TOP LEFT
        pie.separator()

        # TOP RIGHT
        pie.separator()

        # BOTTOM LEFT
        pie.separator()

        # BOTTOM RIGHT
        pie.separator()


class VIEW3D_PT_viewport_rotation_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    # bl_category = "META"
    bl_label = "View Rotation"

    # bl_ui_units_x = 12

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        if context.preferences.inputs.view_rotate_method == 'TRACKBALL':
            col.prop(context.preferences.inputs, "view_rotate_sensitivity_trackball")
        else:
            col.prop(context.preferences.inputs, "view_rotate_sensitivity_turntable")


class VIEW3D_PT_viewport_orbit_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    # bl_category = "META"
    bl_label = "View Rotation"

    # bl_ui_units_x = 12

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        orbit_center_label = "Enable Orbit Selected"
        if context.preferences.inputs.use_rotate_around_active:
            orbit_center_label = "Disable Orbit Selected"

        op = col.operator("wm.context_toggle", text=orbit_center_label)
        op.data_path = "preferences.inputs.use_rotate_around_active"


class VIEW3D_MT_WLT_cursor_pie(Menu):
    bl_label = "WLT Cursor Pie"

    def draw(self, context):
        # region = context.region_data
        layout = self.layout
        # view = context.space_data
        pie = layout.menu_pie()

        # LEFT
        context_op = pie.operator(
            "wlt.context_op",
            text="Move Cursor",
            icon='ORIENTATION_CURSOR'
        )
        context_op.def_op = "transform.translate"
        context_op.def_op_args = "'INVOKE_DEFAULT', True"
        context_op.def_op_props = ("{'cursor_transform': True}")

        context_op.ctrl_op = "view3d.snap_cursor_to_active"
        context_op.ctrl_op_args = "'INVOKE_DEFAULT', True"

        context_op.alt_op = "view3d.snap_cursor_to_selected"
        context_op.alt_op_args = "'INVOKE_DEFAULT', True"
        context_op.alt_op_props = "{'use_offset': False}"

        # RIGHT

        op = pie.operator("wm.call_menu_pie", text="Origin")
        op.name = "VIEW3D_MT_WLT_origin_pie"

        # context_op = pie.operator(
        #     "wlt.context_op",
        #     text="Reset Cursor",
        #     icon='CURSOR'
        # )
        # context_op.def_op = "view3d.snap_cursor_to_center"
        # context_op.def_op_props = ""

        # context_op.ctrl_op = "view3d.snap_cursor_to_active"
        # context_op.ctrl_op_props = ""

        # BOTTOM
        context_op = pie.operator(
            "wlt.context_op",
            text="Cursor: Snap To | Align To | Move",
            icon='PIVOT_CURSOR'
        )
        context_op.def_op = "view3d.snap_cursor_to_selected"
        context_op.def_op_args = "'INVOKE_DEFAULT', True"
        context_op.def_op_props = ""

        context_op.ctrl_op = "wlt.snap_align_cursor"
        context_op.ctrl_op_args = "'INVOKE_DEFAULT', True"
        context_op.ctrl_op_props = "{'move_mode': 'ALIGN_ONLY'}"

        context_op.alt_op = "transform.translate"
        context_op.alt_op_args = "'INVOKE_DEFAULT', True"
        context_op.alt_op_props = ("{'cursor_transform': True}")

        # TOP
        context_op = pie.operator(
            "wlt.context_op",
            text="Selected to Cursor | Active",
            icon='CUBE',
        )
        context_op.def_op = "view3d.snap_selected_to_cursor"
        context_op.def_op_props = "{'use_offset': True}"

        context_op.ctrl_op = "view3d.snap_selected_to_active"
        context_op.ctrl_op_props = ""

        context_op.alt_op = "view3d.snap_selected_to_cursor"
        context_op.alt_op_args = "'INVOKE_DEFAULT', True"
        context_op.alt_op_props = "{'use_offset': False}"

        # TOP LEFT

        # TOP RIGHT
        # pie.prop_enum(context.scene.transform_orientation_slots[1], 'type', value='GLOBAL')

        # BOTTOM LEFT
        # sub = pie.column()
        # sub.operator_context = 'EXEC_DEFAULT'
        # op = sub.operator("transform.select_orientation", text="Global")
        # op.orientation = 'GLOBAL'

        # BOTTOM RIGHT


class VIEW3D_MT_PIE_view_utilities(Menu):
    bl_label = "View Utilities"

    def draw(self, context):
        v3dtheme = context.preferences.themes[0].view_3d
        ws = bpy.context.workspace
        colorz = ws.temp_wires
        # region = context.region_data
        layout = self.layout
        # view = context.space_data
        pie = layout.menu_pie()

        # LEFT
        box = pie.box()
        col = box.column(align=True)

        col.prop(colorz, "default_obj_wire", text="")
        col.prop(colorz, "default_edit_wire", text="")

        op = col.operator("wlt.store_wire_color")

        col.prop(colorz, "temp_obj_wire", text="")
        col.prop(colorz, "temp_edit_wire", text="")

        # RIGHT
        col = pie.column()
        col.prop(v3dtheme, "vertex_size", text="Vertex Size", slider=True)

        # BOTTOM
        col = pie.column()
        op = col.operator("wlt.set_color", text="Toggle Wire Colors")
        op.tog_set = True
        op.sync_wire = True
        op.invert_wire = False
        op.tog_vert_size = False

        # TOP
        col = pie.column()
        op = col.operator("wlt.set_color", text="Toggle Vertex Sizes")
        op.tog_vert_size = True
        op.tog_set = False
        op.sync_wire = False
        op.invert_wire = False
        # TOP LEFT
        # TOP RIGHT
        # BOTTOM LEFT
        # BOTTOM RIGHT

class VIEW3D_MT_WLT_origin_pie(Menu):
    bl_label = "WLT Origin Pie"
    bl_description = "A pie for moving object origins"


    def draw(self, context):
        tool_settings = context.scene.tool_settings
        layout = self.layout
        pie = layout.menu_pie()

        # LEFT
        pie.prop(
            tool_settings,
            "use_transform_data_origin",
            text="Move Origins",
            # icon='TRANSFORM_ORIGINS',
            toggle=True
        )
        # RIGHT
        op = pie.operator(
            "wlt.set_origin",
            text='To Cursor',
        )
        op.snap_mode = 'CURSOR'
        # BOTTOM
        op = pie.operator(
            "wlt.origin_to_bbox",
            text='Bounding Box Bottom',
        )
        op.box_mode = 'FACE'
        op.box_face = 'ZNEG'
        # TOP
        op = pie.operator(
            "wlt.origin_to_bbox",
            text='To Geometry Center',
        )
        op.box_mode = 'FACE'
        op.box_face = 'CENTER'
        # TOP LEFT
        pie.separator()
        # TOP RIGHT
        pie.separator()
        # BOTTOM LEFT
        pie.separator()
        # BOTTOM RIGHT


class VIEW3D_MT_WLT_tablet_pie(Menu):
    bl_label = "WLT Tablet Pie"
    bl_description = "A pie for pen tablet stuff"


    def draw(self, context):
        # region = context.region_data
        layout = self.layout
        pie = layout.menu_pie()

        # LEFT
        op = pie.operator("wm.call_menu_pie", text="Origin")
        op.name = "VIEW3D_MT_WLT_origin_pie"
        # RIGHT
        op = pie.operator("wm.call_menu_pie", text="Cursor")
        op.name = "VIEW3D_MT_WLT_cursor_pie"
        # BOTTOM
        if context.mode == "OBJECT":
            op = pie.operator("wlt.group_select", text="Select Hierachy")
        else:
            op = pie.operator("wlt.super_select", text="Select Topology")
            op.action = "0"
        # TOP
        op = pie.operator("wm.call_menu_pie", text="View")
        op.name = "VIEW3D_MT_WLT_view_pie"
        # TOP LEFT
        pie.separator()
        # TOP RIGHT
        pie.separator()
        # BOTTOM LEFT
        pie.separator()
        # BOTTOM RIGHT
        op = pie.operator("view3d.object_mode_pie_or_toggle", text="Editor Mode")


# I'm trying some stuff in here that's totally unrelated to the actual functionality.
# The variable names are obtuse.

class VIEW3D_PT_camera_list(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_category = "WLT"
    bl_label = "Camera List"
    bl_options = { 'HEADER_LAYOUT_EXPAND',  }

    def draw(self, context):
        C = context
        wm = C.window_manager
        mp_props = context.workspace.WLT
        active = C.active_object
        scene = C.scene

        # Single-letter capitalized variable names....
        L = self.layout
        R = L.column(align=True)

        row = R.row(align=True)
        row.template_list("CUSTOM_UL_camera_list", "", context.blend_data,
                          "cameras", mp_props, "mp_cam_index", rows=1)


def listpanel(C, L):
    wm = C.window_manager
    mp_props = C.workspace.WLT
    active = C.active_object
    scene = C.scene

    # Single-letter capitalized variable names....
    R = L.column(align=True)
    row = R.row(align=True)
    row.template_list("CUSTOM_UL_camera_list", "", C.blend_data,
                        "cameras", mp_props, "mp_cam_index", rows=1)

def listpanel_alt(self, C):
    wm = C.window_manager
    mp_props = C.workspace.WLT
    active = C.active_object
    scene = C.scene

    # Single-letter capitalized variable names....
    L = self.layout.menu_pie()
    L.ui_units_x = 5
    R = L.column(align=True)
    row = R.row(align=True)
    row.template_list("CUSTOM_UL_camera_list", "", C.blend_data,
                        "cameras", mp_props, "mp_cam_index", type='DEFAULT')

def camera_pie_base(self, context):
    region = context.region_data
    layout = self.layout
    # view = context.space_data
    pie = layout.menu_pie()
    event = []

    wm = context.window_manager
    mp_props = context.workspace.WLT

    # LEFT
    listpanel(context, pie)
    # RIGHT
    col = pie.column()
    col.ui_units_x = 5
    col.ui_units_y = 33
    col.template_list("CUSTOM_UL_camera_list", "", context.blend_data,
                            "cameras", mp_props, "mp_cam_index", type="DEFAULT")
    # BOTTOM
    # pie.template_component_menu(mp_props, "fp_tabs", name="jim")
    # wm.popup_menu_pie(event, listpanel_alt,)
    # TOP
    # TOP LEFT
    # TOP RIGHT
    # BOTTOM LEFT
    # BOTTOM RIGHT


class WLT_OT_EnhancedCameraPie(bpy.types.Operator):
    """Shortest Path Pick operator wrapper with a pie menu for fancy things"""
    bl_idname = "wlt.ehc"
    bl_label = "WLT Enhanced Camera Pie"
    bl_description = """Fancy Things"""
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        wm = context.window_manager
        m_loc = (event.mouse_region_x, event.mouse_region_y)
        self.m_loc = m_loc

        wm.popup_menu_pie(event, draw_func=camera_pie_base, title="", icon='NONE')
        return {'FINISHED'}


class VIEW3D_MT_WLT_camera_pie(Menu):
    bl_label = "WLT Camera Pie"

    def draw(self, context):
        region = context.region_data
        layout = self.layout
        # view = context.space_data
        pie = layout.menu_pie()
        event = []

        wm = context.window_manager
        mp_props = context.workspace.WLT

        scene_has_cam = True if context.scene.camera else False

        if not scene_has_cam:
            # LEFT
            pie.separator()
            # RIGHT
            pie.separator()

            if context.mode == 'OBJECT':
                # BOTTOM
                op = pie.operator(
                    "object.camera_add",
                    text="Add Camera"
                )
                op.enter_editmode = False
            else:
                # BOTTOM
                op = pie.operator(
                    "object.editmode_toggle",
                    text="Exit Edit Mode"
                )
        else:
            if not region.view_perspective == 'CAMERA':

                # LEFT
                pie.separator()
                # RIGHT
                pie.separator()

                cam_icon = 'CAMERA_DATA'
                if region.view_perspective == 'CAMERA':
                    cam_icon = 'OUTLINER_OB_CAMERA'

                if context.space_data.lock_camera:
                    cam_icon = 'CON_CAMERASOLVER'

                # BOTTOM
                context_op = pie.operator(
                    "wlt.context_op",
                    text="View Cam | Cam to View | Select Cam",
                    icon=cam_icon
                )

                context_op.def_op = "view3d.view_camera"
                context_op.def_op_args = "'INVOKE_DEFAULT', True,"
                context_op.def_op_props = ""

                context_op.ctrl_op = "view3d.camera_to_view"
                context_op.ctrl_op_args = "'INVOKE_DEFAULT', True,"
                context_op.ctrl_op_props = ""

                context_op.shift_op = "object.select_camera"
                context_op.shift_op_args = "'INVOKE_DEFAULT', True,"
                context_op.shift_op_props = ""
            else:
                # LEFT
                pie.operator(
                    "ui.eyedropper_depth",
                    text="Set Focal Depth"
                )

                # RIGHT
                op = pie.operator(
                    "wm.context_modal_mouse",
                    text="Zoom"
                )
                op.data_path_iter = "selected_editable_objects"
                op.data_path_item = "data.lens"
                op.input_scale = 0.1
                op.header_text = "Camera Lens Angle: %.1fmm"

                # BOTTOM
                pie.operator(
                    "object.select_camera",
                    text="Select Camera"
                )

                # TOP
                row = pie.row(align=True)

                if context.scene.keying_sets.active:
                    row.operator(
                        'anim.keyframe_insert',
                        text='',
                        icon='KEY_HLT'
                    )
                    row.operator("screen.keyframe_jump", text="", icon='PREV_KEYFRAME').next = False

                    sub = row.row(align=True)
                    sub.scale_x = 0.75
                    sub.prop(
                        context.scene,
                        "frame_current",
                        text=""
                    )

                    row.operator("screen.keyframe_jump", text="", icon='NEXT_KEYFRAME').next = True
                    row.operator(
                        'anim.keyframe_delete',
                        text='',
                        icon='KEY_DEHLT'
                    )
                else:
                    row.prop_search(
                        context.scene.keying_sets,
                        "active",
                        context.scene,
                        "keying_sets",
                        text="",
                        )
                    row.operator(
                        'wlt.add_camera_keyset',
                        text='Add Keyingset',
                        icon='KEYINGSET'
                    )
        # TOP LEFT
        # TOP RIGHT
        # BOTTOM LEFT
        # BOTTOM RIGHT

OUT = [
    VIEW3D_MT_WLT_view_pie,
    VIEW3D_MT_WLT_orbit_pie,
    VIEW3D_MT_WLT_cursor_pie,
    VIEW3D_MT_PIE_view_utilities,
    VIEW3D_PT_viewport_rotation_panel,
    VIEW3D_PT_viewport_orbit_panel,
    VIEW3D_MT_WLT_tablet_pie,
    VIEW3D_MT_WLT_origin_pie,
    VIEW3D_MT_WLT_camera_pie,
    WLT_OT_EnhancedCameraPie,
]