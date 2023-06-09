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
    Curve,
    SurfaceCurve
)

from ..utilities.WidthFunc import (
    get_breakpoints,
    # get_width_factor,
    check_width,
    get_break_full
)

from ..utilities.DeepInspect import (
    isModalRunning,
    peekKeyQueue,
    isTablet,
)

from ..preferences import (
    get_prefs
)

from bl_ui.space_toolsystem_toolbar import (
    VIEW3D_PT_tools_active as view3d_tools
)
from bpy_extras.node_utils import find_node_input

def active_tool():
    return view3d_tools.tool_active_from_context(bpy.context)


class CUSTOM_UL_camera_list(bpy.types.UIList):
    EMPTY = 1 << 0

    use_filter_empty: bpy.props.BoolProperty(
        name="Filter Unused",
        default=True,
        options=set(),
        description="Whether to filter cameras with zero users",
    )
    use_filter_empty_reverse: bpy.props.BoolProperty(
        name="Reverse Empty",
        default=False,
        options=set(),
        description="Reverse empty filtering",
    )
    use_filter_name_reverse: bpy.props.BoolProperty(
        name="Reverse Name",
        default=False,
        options=set(),
        description="Reverse name filtering",
    )

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        split = layout.row(align=True)

        user = None
        for obj in bpy.data.objects:
            if obj.data == item:
                user = obj
                break

        name = split.row(align=True)

        if user:
            name.prop(
                user,
                "name",
                text=""
                )

            if bpy.context.view_layer.objects.active and bpy.context.view_layer.objects.active.name == user.name:
                sel_icon = 'RESTRICT_SELECT_OFF'
            else:
                sel_icon = 'RESTRICT_SELECT_ON'

            if context.scene.camera and context.scene.camera.name == user.name:
                icon = 'RADIOBUT_ON'
            else:
                icon = 'RADIOBUT_OFF'

            buttons = split.row(align=True)

            op = buttons.operator(
                "wm.context_set_id",
                text="",
                icon=icon
            )
            op.data_path = "scene.camera"
            op.value = str(user.name)

            op = buttons.operator(
                "wlt.zoop",
                text="",
                icon='SNAP_FACE_CENTER'
            )
            op.target_camera = str(user.name)

            op = buttons.operator(
                "wlt.object_select",
                text="",
                icon=sel_icon
            )
            op.target_object = str(user.name)

    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        row = layout.row()
        row.alignment = 'RIGHT'

    def filter_items(self, context, data, propname):

        cams_datablocks = getattr(data, propname)
        flt_flags = []
        flt_neworder = []

        helper_funcs = bpy.types.UI_UL_list

        cams = []
        for obj in bpy.data.objects:
            for cam in cams_datablocks:
                if obj.data == cam:
                    cams.append(obj)
                    # break

        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, cams_datablocks, "name",
                                                          reverse=self.use_filter_name_reverse)
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(cams_datablocks)

        # Filter by emptiness.
        if self.use_filter_empty:
            for i, cam in enumerate(cams_datablocks):
                if cam.users < 1:
                    flt_flags[i] |= ~self.EMPTY

        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(cams_datablocks)

        return flt_flags, flt_neworder


# Did some cut-and-burn reorganizing here,
# breaking things up into functions and reducing
# the overall indentation.
# I still need to go through and remove redundant
# variable declarations and clean up the naming

def transform_tab(layout, context):
    active_obj = context.view_layer.objects.active
    wm = bpy.context.window_manager
    WLT_props = context.workspace.WLT

    if not WLT_props.mp_tabs:
        WLT_props.mp_tabs = '0'

    # Aliased Stuff
    scene = context.scene
    tool_settings = context.scene.tool_settings

    units = scene.unit_settings
    overlay = context.space_data.overlay
    v3dtheme = context.preferences.themes[0].view_3d

    bcol = layout

    orient_slot = scene.transform_orientation_slots[0]

    # Group 1 - Transform Orientation and Pivot
    label_row = bcol.row(align=True)

    label_left = label_row.row(align=True)
    label_left.alignment = 'LEFT'
    label_left.label(text="Orientation")

    label_right = label_row.row(align=True)
    label_right.alignment = 'RIGHT'
    label_right.emboss = 'NONE'
    op = label_right.operator("wlt.tool_tip", text="", icon='INFO')
    op.tooltip = (
                "The A-F buttons are a series of custom transform quick slots. \n"
                "You can use them to swap saved orientations out of a shared slot. \n"
                "This system is mostly meant to manage UI clutter"
    )

    flow = bcol.grid_flow(align=True)

    flow.prop_enum(
                orient_slot,
                "type",
                'GLOBAL',
                text=""
                )
    flow.prop_enum(
                orient_slot,
                "type",
                'LOCAL',
                text=""
                )
    flow.prop_enum(
                orient_slot,
                "type",
                'NORMAL',
                text=""
                )
    flow.prop_enum(
                orient_slot,
                "type",
                'CURSOR',
                text=""
                )
    flow.prop_enum(
                orient_slot,
                "type",
                'GIMBAL',
                text=""
                )
    flow.prop_enum(
                orient_slot,
                "type",
                'VIEW',
                text=""
                )

    flow = bcol.grid_flow(align=True)
    # flow.scale_y = 0.5

    flow.operator(
        "wlt.make_named_orientation",
        text="",
        icon='EVENT_A'
    ).transform_slot = 'SLOT_A'
    flow.operator(
        "wlt.make_named_orientation",
        text="",
        icon='EVENT_B'
    ).transform_slot = 'SLOT_B'
    flow.operator(
        "wlt.make_named_orientation",
        text="",
        icon='EVENT_C'
    ).transform_slot = 'SLOT_C'
    flow.operator(
        "wlt.make_named_orientation",
        text="",
        icon='EVENT_D'
    ).transform_slot = 'SLOT_D'
    flow.operator(
        "wlt.make_named_orientation",
        text="",
        icon='EVENT_E'
    ).transform_slot = 'SLOT_E'
    flow.operator(
        "wlt.make_named_orientation",
        text="",
        icon='EVENT_F'
    ).transform_slot = 'SLOT_E'

    bcol.separator()

    # Group 2 - Pivot
    labeltext = "Pivot"

    bcol.label(text=labeltext)

    row = bcol.row(align=True)
    row.prop(
        tool_settings,
        "transform_pivot_point",
        text="",
        expand=False
    )
    row.prop(
        tool_settings,
        "use_transform_data_origin",
        text="",
        icon='TRANSFORM_ORIGINS',
        toggle=True
    )
    row.prop(
        tool_settings,
        "use_transform_pivot_point_align",
        text="",
        icon='CON_PIVOT',
        toggle=True
    )
    row.prop(
        tool_settings,
        "use_transform_skip_children",
        text="",
        icon='CON_CHILDOF',
        toggle=True
    )

    row = bcol.row(align=True)

    row.operator(
        "wlt.align_cursor_to_orientation",
        text="Do Cursor",
    )

    row.operator_context = 'EXEC_REGION_WIN'

    op = row.operator(
        "transform.transform",
        text="Do Object",
    )
    op.mode = 'ALIGN'

    flow.operator_context = 'INVOKE_DEFAULT'

    bcol.separator()
    header_row = bcol.row(align=True)
    header_row.label(text="Quick Origin")
    header_row.menu("VIEW3D_MT_set_origin", icon='PROPERTIES', text="")
    # bcol.label(text="Quick Origin")

    grid = bcol.grid_flow(columns=2, row_major=True, align=True, even_columns=True, even_rows=False)
    grid.scale_y = 0.75

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

    # Group 2 - Proportional Editing

    bcol.separator()
    bcol.label(text="Proportional Editing")

    g2 = bcol.grid_flow(columns=1, align=True)
    g2.separator(factor=0.25)
    row = g2.row(align=True)
    # row.alignment = 'CENTER'

    obj = context.active_object
    object_mode = 'OBJECT' if obj is None else obj.mode

    # Copied from space_view3d.py
    if object_mode in {'EDIT', 'PARTICLE_EDIT', 'SCULPT_GPENCIL', 'EDIT_GPENCIL', 'OBJECT'}:
        kw = {}
        if object_mode == 'OBJECT':
            attr = "use_proportional_edit_objects"
        else:
            attr = "use_proportional_edit"

            if tool_settings.use_proportional_edit:
                if tool_settings.use_proportional_connected:
                    kw["icon"] = 'PROP_CON'
                elif tool_settings.use_proportional_projected:
                    kw["icon"] = 'PROP_PROJECTED'
                else:
                    kw["icon"] = 'PROP_ON'
            else:
                kw["icon"] = 'PROP_OFF'

        proport_label = "Falloff"
        if tool_settings.proportional_edit_falloff == 'SMOOTH':
            proport_label = "Smooth"
        elif tool_settings.proportional_edit_falloff == 'SPHERE':
            proport_label = "Sphere"
        elif tool_settings.proportional_edit_falloff == 'ROOT':
            proport_label = "Root"
        elif tool_settings.proportional_edit_falloff == 'INVERSE_SQUARE':
            proport_label = "Inverse Square"
        elif tool_settings.proportional_edit_falloff == 'SHARP':
            proport_label = "Sharp"
        elif tool_settings.proportional_edit_falloff == 'LINEAR':
            proport_label = "Linear"
        elif tool_settings.proportional_edit_falloff == 'CONSTANT':
            proport_label = "Constant"
        elif tool_settings.proportional_edit_falloff == 'RANDOM':
            proport_label = "Random"

        exp = False
        g2_check = check_width('UI', 11, 1, 440)
        proport_label = ""
        if not g2_check[0]:
            exp = False
            proport_label = ""

        row.prop(tool_settings, attr, text=proport_label, icon_only=True, **kw)
        row.prop(tool_settings, "proportional_edit_falloff", expand=exp, text="")
        quarg = (True if context.mode != 'OBJECT' else False)

        flow_t = (2, 3, 6)
        flow_v = (1, 1, 2)
        flow_cols = get_breakpoints('UI', flow_t, flow_v)

        flow = g2.grid_flow(columns=flow_cols[0], align=True)
        flow.active = quarg
        flow.prop(
            tool_settings,
            "use_proportional_connected",
            text="Connected",
            toggle=True
        )
        flow.prop(
            tool_settings,
            "use_proportional_projected",
            text="Project",
            toggle=True
        )

    # Group 3 - Snapping
    bcol.separator()
    bcol.label(text="Snapping")

    g3 = bcol.grid_flow(columns=1, align=True)
    g3.separator(factor=0.25)
    row = g3.row(align=True)

    bcr1_t = (6, 8, 12)
    bcr1_v = (1, 1, 1)
    bcr1_cols = get_breakpoints('UI', bcr1_t, bcr1_v)
    bcol_rg1 = row.grid_flow(columns=bcr1_cols[0], align=True)

    bcol_rg1 = row.row(align=True)

    # Row 1 Sub 1
    bcr1_s1_t = (2, 5, 8)
    bcr1_s1_v = (2, 4, 8)
    bcr1_s1_cols = get_breakpoints('UI', bcr1_s1_t, bcr1_s1_v)
    bcr1_s1_cols = get_break_full('UI', bcr1_s1_t, bcr1_s1_v, '>=', False, True)

    snp_elem = "bcol_row1_sub1.prop(tool_settings, 'snap_elements', text='', expand=False)"
    if bcr1_s1_cols[5] < 20:
        snp_elem = "bcol_row1_sub1.prop_menu_enum(tool_settings, 'snap_elements')"

    bcol_row1_sub1 = bcol_rg1.grid_flow(
                                    columns=bcr1_s1_cols[0],
                                    align=True
    )

    bcol_row1_sub1 = bcol_rg1.grid_flow(columns=8, align=True)
    exec(snp_elem)

    sub_row = row.row(align=True)

    sub_row.prop(
                tool_settings,
                "use_snap_project",
                text="",
                icon='MOD_SHRINKWRAP',
                toggle=True
    )
    sub_row.prop(
                tool_settings,
                "use_snap_align_rotation",
                text="",
                icon='CON_SHRINKWRAP',
                toggle=True
    )
    sub_row.prop(
                tool_settings,
                "use_snap_peel_object",
                text="",
                icon='MOD_SOLIDIFY',
                toggle=True
    )

    row = g3.row(align=True)
    left = row.row(align=True)
    left.prop(tool_settings, "snap_target", text="")

    right = row.row(align=True)

    right.prop(
                tool_settings,
                "use_snap_rotate",
                text="",
                icon='FORCE_CURVE',
                toggle=True
    )
    right.prop(
                tool_settings,
                "use_snap_translate",
                text="",
                icon='CON_LOCLIKE',
                toggle=True
    )
    right.prop(
                tool_settings,
                "use_snap_grid_absolute",
                text="",
                icon='SNAP_GRID',
                toggle=True
    )

    # Group 4 - Grid

    bcol.separator()
    bcol.label(text="Grid")
    group = bcol.grid_flow(columns=1, align=True)
    # group.separator(factor=0.25)

    row = group.split(factor=0.5, align=True)

    left = row.row(align=True)
    left.prop(overlay, "grid_scale")

    right = row.row(align=True)
    # right.prop(overlay, "show_floor", toggle=True, text="Floor")
    right.prop(units, "length_unit", text="")

    row = group.split(factor=0.5, align=True)

    left = row.row(align=True)
    left.prop(overlay, "show_ortho_grid", toggle=True, text="Ortho Grid")

    right = row.split(factor=0.5, align=True)
    right.prop(overlay, "show_floor", toggle=True, text="Floor")

    right.prop(overlay, "show_axis_x", toggle=True, text="X")
    right.prop(overlay, "show_axis_y", toggle=True, text="Y")
    right.prop(overlay, "show_axis_z", toggle=True, text="Z")


def camera_tab(layout, context):
    active_obj = context.view_layer.objects.active
    wm = bpy.context.window_manager
    WLT_props = context.workspace.WLT
    cam_sections = WLT_props.mp_cam_sections

    if not WLT_props.mp_tabs:
        WLT_props.mp_tabs = '0'

    # Aliased Stuff
    scene = context.scene
    bcol = layout

    orient_slot = scene.transform_orientation_slots[0]

    bcol.label(text="Scene Cameras:")

    row = bcol.row(align=True)
    row.template_list("CUSTOM_UL_camera_list", "", context.blend_data, "cameras", WLT_props, "mp_cam_index", rows=1, maxrows=4)

    if active_obj and active_obj.type == 'CAMERA':
        camera = active_obj
    elif context.space_data.region_3d.view_perspective == 'CAMERA':
        camera = context.space_data.camera
    else:
        camera = None

    if camera:
        bcol.label(text="Selected Camera:")

        if context.scene.camera and context.scene.camera.name == camera.name:
            icon = 'RADIOBUT_ON'
        else:
            icon = 'RADIOBUT_OFF'

        row = bcol.row(align=True)
        

        row.prop(
            camera,
            "name",
            text=""
            )
        row.separator()
        sub = row.row(align=True)
        op = sub.operator(
            "wm.context_set_id",
            text="",
            icon=icon
        )
        op.data_path = "scene.camera"
        op.value = str(camera.name)

        op = sub.operator(
            "wlt.zoop",
            text="",
            icon='SNAP_FACE_CENTER')

        op.target_camera = str(camera.name)


        row = bcol.row(align=True)

        row.prop(
            camera.data,
            'show_limits',
            text="Limits",
            toggle=True
        )
        row.prop(
            camera.data,
            'show_mist',
            text="Mist",
            toggle=True
        )
        row.prop(
            camera.data,
            'show_sensor',
            text="Sensor",
            toggle=True
        )
        row.prop(
            camera.data,
            'show_name',
            text="Name",
            toggle=True
        )

        row = bcol.row(align=True)
        row.prop(
            camera.data,
            'display_size',
            text="Display Size",
        )

        sub = bcol.row(align=True)
        sub.prop(
            camera.data,
            'show_passepartout',
            text="Dim Outer",
            toggle=True
        )
        sub.prop(
            camera.data,
            'passepartout_alpha',
            text="",
        )

        row = bcol.row(align=False)
        row.emboss = 'NONE'
        row.prop_enum(
            WLT_props,
            'mp_cam_sections',
            '0',
            text='Settings',
            icon='TRIA_DOWN' if '0' in cam_sections else 'TRIA_RIGHT'
        )

        if '0' in cam_sections:
            col = bcol.column(align=True)

            sub = col.row(align=True)

            if camera.data.sensor_fit == 'AUTO':
                sub.prop(
                    camera.data,
                    'sensor_width',
                    text="Sensor Size",
                )
            elif camera.data.sensor_fit == 'HORIZONTAL':
                sub.prop(
                    camera.data,
                    'sensor_width',
                    text="Sensor Width",
                )
            elif camera.data.sensor_fit == 'VERTICAL':
                sub.prop(
                    camera.data,
                    'sensor_height',
                    text="Sensor Height",
                )

            op = sub.operator(
                "wm.context_cycle_enum",
                text="",
                icon='CON_SIZELIKE'
            )
            op.data_path = "object.data.sensor_fit"
            op.wrap = True

            sub = col.row(align=True)

            if camera.data.lens_unit == 'MILLIMETERS':
                sub.prop(
                    camera.data,
                    'lens',
                )

                sub.prop_enum(
                    camera.data,
                    'lens_unit',
                    'FOV',
                    text='',
                    icon='SNAP_INCREMENT'
                )
            else:
                sub.prop(
                    camera.data,
                    'angle',
                )
                sub.prop_enum(
                    camera.data,
                    'lens_unit',
                    'MILLIMETERS',
                    text='',
                    icon='LINCURVE'
                )

            col = bcol.column(align=True)
            sub = col.row(align=True)

            sub.prop(
                camera.data,
                'clip_start'
            )

            sub.prop(
                camera.data,
                'clip_end'
            )

            col = bcol.column(align=True)
            sub = col.row(align=True)

            sub.prop(
                camera.data,
                'shift_x'
            )

            sub.prop(
                camera.data,
                'shift_y'
            )

            col = bcol.column(align=True)

            col.prop(
                scene.render,
                'resolution_x'
            )
            col.prop(
                scene.render,
                'resolution_y'
            )
            col.prop(
                scene.render,
                'resolution_percentage'
            )



        row = bcol.row(align=False)
        row.emboss = 'NONE'
        row.prop_enum(
            WLT_props,
            'mp_cam_sections',
            '1',
            text='Actions',
            icon='TRIA_DOWN' if '1' in cam_sections else 'TRIA_RIGHT'
        )

        if '1' in cam_sections:
            col = bcol.column(align=True)
            sub = col.row(align=True)

            if context.scene.keying_sets.active:
                sub.prop_search(
                    context.scene.keying_sets,
                    "active",
                    context.scene,
                    "keying_sets",
                    text="",
                    )

            sub.operator(
                'wlt.add_camera_keyset',
                text='',
                icon='KEYINGSET'
            )
            sub.operator(
                'anim.keyframe_insert',
                text='',
                icon='KEY_HLT'
            )
            sub.operator(
                'anim.keyframe_delete',
                text='',
                icon='KEY_DEHLT'
            )

            sub = col.row(align=True)

            sub.prop(
                context.space_data,
                'lock_camera',
                text="Track Camera to View",
                toggle=True
            )

            sub = col.row(align=True)

            sub.operator(
                "view3d.zoom_camera_1_to_1",
                text="1:1"
            )
            sub.operator(
                "view3d.view_center_camera",
                text="Recenter"
            )

            if False in camera.lock_location or False in camera.lock_rotation:
                op_text = "Lock"
                tog = False
            else:
                op_text = "Unlock"
                tog = True

            subsub = sub.row(align=True)
            subsub.alert = tog

            op = subsub.operator(
                "wlt.lock_camera",
                text=op_text,
                # depress=tog
            )
            op.target_object = str(camera.name)

            sub = col.row(align=True)
            sub.operator(
                "view3d.view_selected",
                text="Zoop",
            )
            sub.operator(
                "view3d.zoom_border",
                text="Zoom"
            )
            sub.operator(
                "view3d.walk",
                text="Walk"
            )

        row = bcol.row(align=False)
        row.emboss = 'NONE'
        row.prop_enum(
            WLT_props,
            'mp_cam_sections',
            '2',
            text='Transform',
            icon='TRIA_DOWN' if '2' in cam_sections else 'TRIA_RIGHT'
        )

        if '2' in cam_sections:
            col = bcol.column(align=True)
            col.scale_y = 0.75
            col.prop(
                camera,
                'location',
            )

            col = bcol.column(align=True)
            col.scale_y = 0.75
            if camera.rotation_mode == 'QUATERNION':
                col.prop(
                    camera,
                    'rotation_quaternion',
                )
            elif camera.rotation_mode == 'AXIS_ANGLE':
                col.prop(
                    camera,
                    'rotation_axis_angle',
                )
            else:
                col.prop(
                    camera,
                    'rotation_euler',
                )

        bcol.label(text="Overlays:")

        col = bcol.column(align=True)
        sub = col.row(align=True)

        sub.prop(
            camera.data,
            'show_composition_thirds',
            text="Thirds",
            toggle=True
        )
        sub.prop(
            camera.data,
            'show_composition_center',
            text="Center",
            toggle=True
        )
        sub.prop(
            camera.data,
            'show_composition_golden',
            text="Phi",
            toggle=True
        )


def shading_tab(layout, context):
    active_obj = context.view_layer.objects.active
    wm = bpy.context.window_manager
    WLT_props = context.workspace.WLT

    if not WLT_props.mp_tabs:
        WLT_props.mp_tabs = '0'

    # Aliased Stuff
    scene = context.scene
    tool_settings = context.scene.tool_settings

    units = scene.unit_settings
    overlay = context.space_data.overlay
    v3dtheme = context.preferences.themes[0].view_3d

    bcol = layout

    orient_slot = scene.transform_orientation_slots[0]

    view = context.space_data
    if view.type == 'VIEW_3D':
        shading = view.shading
    else:
        shading = context.scene.display.shading

    overlay = context.space_data.overlay

    active_mat = None
    if active_obj:
        if active_obj.type == 'MESH':
            active_mat = active_obj.active_material

    group = bcol.column(align=True)
    group.active = (True if shading.type in {'SOLID'} else False)
    group.scale_y = 1

    row = group.row(align=True)
    col = row.column(align=True)
    col.ui_units_x = 3.75

    col.prop(shading, "light", expand=True)
    if shading.light == 'MATCAP':
        col_sub = col.row(align=True)
        col_sub.operator(
                            "view3d.toggle_matcap_flip",
                            text="Flip",
                            icon='ARROW_LEFTRIGHT'
                            )
        col_sub.operator("preferences.studiolight_show", text="", icon='PREFERENCES')
    if shading.light == 'STUDIO':
        col_sub = col.row(align=True)
        col_sub.prop(
                        shading,
                        "use_world_space_lighting",
                        text="",
                        toggle=True,
                        icon='WORLD'
                        )
        col_sub.prop(
                        shading,
                        "studiolight_rotate_z",
                        text=""
                        )

    sub_col = row.column(align=True)
    sub_col.enabled = (True if shading.light in {'MATCAP', 'STUDIO'} else False)
    scale = (4 if shading.light in {'MATCAP', 'STUDIO'} else 3)
    sub_col.template_icon_view(
        shading,
        "studio_light",
        scale=scale,
        scale_popup=3
    )

    bcol.label(text="Color")

    group = bcol.split(factor=0.75, align=True)

    group_left = group.column(align=True)
    group_left.scale_y = 1

    shade_mode = " "
    shade_submodes = ('SINGLE', 'OBJECT', 'RANDOM', 'MATERIAL', 'VERTEX', 'TEXTURE')
    shade_len = 3

    if shading.type == 'SOLID':
        shade_mode = "color_type"
        sub_row = group_left.row(align=True)
    elif shading.type == 'WIREFRAME':
        shade_mode = "wireframe_color_type"
        sub_row = group_left.row(align=True)
        group_left.scale_y = 2
    else:
        shade_mode = "color_type"
        sub_row = group_left.row(align=True)

    if shading.type == 'SOLID' or shading.type == 'WIREFRAME':
        for i in range(0, shade_len):
            sub_row.prop_enum(
                shading, shade_mode, shade_submodes[i]
            )

        if shading.type == 'SOLID':
            sub_row = group_left.row(align=True)
            for i in range(0, shade_len):
                sub_row.prop_enum(
                    shading, shade_mode, shade_submodes[i+3]
                )

    flow = group.grid_flow(align=True)
    flow.scale_y = 2

    if shading.type == 'WIREFRAME':
        if shading.wireframe_color_type == 'SINGLE':
            flow.prop(v3dtheme, "wire", text="")
        elif (shading.wireframe_color_type == 'OBJECT'
                and active_obj.type == 'MESH'):
            flow.prop(active_obj, "color", text="")

    if (shading.type == 'SOLID' and active_obj):
        if shading.color_type == 'SINGLE':
            flow.prop(shading, "single_color", text="")
        elif (shading.color_type == 'OBJECT'
                and active_obj.type == 'MESH'):
            flow.prop(active_obj, "color", text="")
        elif (shading.color_type == 'MATERIAL'
                and active_obj.type == 'MESH'):
            if active_obj.active_material:
                flow.prop(active_mat, "diffuse_color", text="")
                if shading.light == 'STUDIO':
                    col = bcol.row(align=True)
                    col.prop(active_mat, "metallic", text="Metalic")
                    col.prop(active_mat, "roughness", text="Rougness")

    # $$Xray
    bcol.label(text="X-Ray")
    row = bcol.row(align=True)

    row_left = row.column(align=True)
    row_left.scale_y = 2

    ico = ('CUBE' if shading.show_xray else 'MESH_CUBE')
    row_left.prop(shading, "show_xray", text="", toggle=True, icon=ico)

    row_right = row.column(align=True)
    row_right.scale_y = 1
    row_right.active = shading.show_xray

    row_right.prop(shading, "xray_alpha")
    row_right.prop(overlay, "backwire_opacity")

    # $$Cavity
    bcol.label(text="Cavity")
    c_col = bcol.column(align=True)

    row = c_col.row(align=True)

    press1 = (True if shading.cavity_type
                in {'WORLD', 'BOTH'}
                and shading.show_cavity else False)

    press2 = (True if shading.cavity_type
                in {'SCREEN', 'BOTH'}
                and shading.show_cavity else False)

    ico = ('WORLD_DATA' if WLT_props.mp_shading_cavtoggle[1] else 'WORLD_DATA')
    op = row.operator("wlt.bool_to_enum", text="", icon=ico, depress=press1)
    op.bool_prop = 'window_manager.wlt.mp_shading_cavtoggle'
    op.enum_prop_path = 'space_data.shading.cavity_type'
    op.bool_index = 1

    sub = row.split(factor=0.45, align=True)
    sub.active = press1

    sub_sub = sub.row(align=True)
    sub_sub.prop(shading, "cavity_ridge_factor", text="Ridge", icon='WORLD')
    sub_sub = sub.row(align=True)
    sub_sub.prop(shading, "cavity_valley_factor", text="Valley", icon='WORLD')
    sub_sub.popover(
        panel="VIEW3D_PT_shading_options_ssao",
        icon='PREFERENCES',
        text="",
    )

    row = c_col.row(align=True)

    ico = ('RESTRICT_VIEW_OFF' if WLT_props.mp_shading_cavtoggle[0] else 'RESTRICT_VIEW_ON')

    op = row.operator("wlt.bool_to_enum", text="", icon=ico, depress=press2)
    op.bool_prop = 'window_manager.WLT_props.mp_shading_cavtoggle'
    op.enum_prop_path = 'space_data.shading.cavity_type'
    op.bool_index = 0

    sub = row.row(align=True)
    sub.active = press2

    sub.prop(shading, "curvature_ridge_factor", text="Ridge")
    sub.prop(shading, "curvature_valley_factor", text="Valley")

    # $$Lighting
    bcol.label(text="Shadow")

    row = bcol.row(align=True)
    row.prop(shading, "show_shadows", text="", icon='LIGHT_HEMI')

    sub_row = row.row(align=True)
    sub_row.active = shading.show_shadows

    sub_row.prop(shading, "shadow_intensity", text="Shadow Intensity")

    sub_row.popover(
        panel="VIEW3D_PT_shading_options_shadow",
        icon='PREFERENCES',
        text="",
    )

    # $$Background Color
    # TODO: Fix Naming
    bcol.label(text="Background")

    if shading.background_type == 'VIEWPORT':

        bck_row = bcol.split(factor=0.75, align=True)
        bck_row_left = bck_row.row(align=True)
        bck_row_left.prop(shading, "background_type", expand=True)

        bck_row_right = bck_row.row(align=True)

        bck_row_right.prop(shading, "background_color", text="")

    if shading.background_type == 'THEME':

        bck_row = bcol.split(factor=0.75, align=True)

        bck_row_left = bck_row.row(align=True)
        bck_row_left.prop(shading, "background_type", expand=True)

        bck_row_right = bck_row.row(align=True)

        v3dtheme_gradient = context.preferences.themes[0].view_3d.space.gradients
        bck_row_right.prop(v3dtheme_gradient, "high_gradient", text="")

    if shading.background_type == 'WORLD':
        world = context.scene.world

        bck_row = bcol.row(align=True)

        bck_row_left = bck_row.row(align=True)
        bck_row_left.prop(shading, "background_type", expand=True)

        bck_row_right = bck_row.row(align=True)

        wrld_row = bcol.column(align=True)
        wrld_row.prop(world, "use_nodes", text="↓ Use Nodes ↓", toggle=True)
        wrld_row.separator()

        if world.use_nodes:
            ntree = world.node_tree
            node = ntree.get_output_node('EEVEE')

            if node:
                input = find_node_input(node, 'Surface')
                if input:
                    node_row = bcol.column(align=True)
                    node_row.template_node_view(ntree, node, input)
                else:
                    bck_row_right.label(text="Incompatible output node")
            else:
                bck_row_right.label(text="No output node")
        else:
            bck_row_right.prop(world, "color", text="")

    # $$Options
    bcol.label(text="Options")

    split = bcol.split(factor=0.725, align=True)

    left = split.row(align=True)
    left.alignment = 'LEFT'

    ico = ('CHECKBOX_HLT' if shading.show_object_outline else 'CHECKBOX_DEHLT')
    left.prop(
                shading,
                "show_object_outline",
                text="Object Outlines",
                toggle=True,
                icon=ico,
                emboss=False
                )

    right = split.row(align=True)
    right.prop(shading, "object_outline_color", text="")

    row = bcol.row(align=True)
    row.alignment = 'LEFT'

    ico = ('CHECKBOX_HLT' if shading.show_backface_culling else 'CHECKBOX_DEHLT')
    row.prop(shading, "show_backface_culling", icon=ico, emboss=False)

    row = bcol.row(align=True)
    row.alignment = 'LEFT'

    ico = ('CHECKBOX_HLT' if shading.use_dof else 'CHECKBOX_DEHLT')
    row.prop(shading, "use_dof", toggle=True, icon=ico, emboss=False)

    row = bcol.row(align=True)
    row.alignment = 'LEFT'

    ico = ('CHECKBOX_HLT' if shading.show_specular_highlight else 'CHECKBOX_DEHLT')
    row.prop(
                shading,
                "show_specular_highlight",
                text="Specular Highlights",
                icon=ico,
                toggle=True,
                emboss=False
                )


def active_obj_tab(layout, context):

    active_obj = context.view_layer.objects.active
    wm = bpy.context.window_manager
    WLT_props = context.workspace.WLT

    if not WLT_props.mp_tabs:
        WLT_props.mp_tabs = '0'

    # Aliased Stuff
    scene = context.scene
    tool_settings = context.scene.tool_settings

    units = scene.unit_settings
    overlay = context.space_data.overlay
    v3dtheme = context.preferences.themes[0].view_3d

    bcol = layout

    orient_slot = scene.transform_orientation_slots[0]

    view = context.space_data
    if view.type == 'VIEW_3D':
        shading = view.shading
    else:
        shading = context.scene.display.shading

    overlay = context.space_data.overlay

    ocol = bcol.column(align=True)
    row = ocol.row(align=True)
    row.template_ID(context.view_layer.objects, "active", filter='AVAILABLE')

    row = ocol.row(align=True)

    if active_obj and (active_obj.type == 'MESH'):

        ocol.label(text="Display As:")

        row_width_check = check_width('UI', 10, 1, 440)

        row_labels = [
                    ("Bounds", " "),
                    ("Wire", " "),
                    ("Solid", " "),
                    ("Textured", " "),
        ]

        row_icons = [
                    ('NONE', 'MESH_CUBE'),
                    ('NONE', 'SHADING_WIRE'),
                    ('NONE', 'SHADING_SOLID'),
                    ('NONE', 'SHADING_TEXTURE'),
        ]

        label_tog = 0
        row_cols = 3
        if not row_width_check[0]:
            label_tog = 1

        row = ocol.row(align=True)

        row.prop_enum(
                    context.object,
                    'display_type',
                    'BOUNDS',
                    text=row_labels[0][label_tog],
                    icon=row_icons[0][label_tog]
                    )

        row.prop_enum(
                    context.object,
                    'display_type',
                    'WIRE',
                    text=row_labels[1][label_tog],
                    icon=row_icons[1][label_tog]
                    )

        row.prop_enum(
                    context.object,
                    'display_type',
                    'SOLID',
                    text=row_labels[2][label_tog],
                    icon=row_icons[2][label_tog]
                    )

        row.prop_enum(
                    context.object,
                    'display_type',
                    'TEXTURED',
                    text=row_labels[3][label_tog],
                    icon=row_icons[3][label_tog]
                    )

        row = ocol.row(align=True)

        shade_mode = "space_data.shading.color_type"

        if shading.type == 'SOLID':
            shade_mode = "space_data.shading.color_type"
            if (shading.color_type == 'OBJECT'):
                label = "Object Color"
            elif (shading.color_type == 'SINGLE'):
                label = "Single Color"
            elif (shading.color_type == 'MATERIAL'):
                label = "Material Color"
            elif (shading.color_type == 'VERTEX'):
                label = "Vertex Color"
            elif (shading.color_type == 'RANDOM'):
                label = "Random Color"
            elif (shading.color_type == 'TEXTURE'):
                label = "Texture"
            else:
                label = "ERROR"
        elif shading.type == 'WIREFRAME':
            shade_mode = "space_data.shading.wireframe_color_type"
            if (shading.wireframe_color_type == 'OBJECT'):
                label = "Object Color"
            elif (shading.wireframe_color_type == 'SINGLE'):
                label = "Single Color"
            else:
                label = "ERROR"
        else:
            label = "No."
        # elif shading.type == 'MATERIAL':

        if shading.type == 'SOLID':
            row.prop(
                context.space_data.shading,
                "color_type",
                text="",
                expand=False
            )

            if (shading.color_type == 'OBJECT'):
                row.prop(
                    context.object,
                    'color',
                    text="",
                )
            elif (shading.color_type == 'SINGLE'):
                row.prop(
                    shading,
                    "single_color",
                    text="")
            elif (shading.color_type == 'MATERIAL'
                    and active_obj.type == 'MESH'):
                if active_obj.active_material:
                    row.prop(
                        active_obj.active_material,
                        "diffuse_color",
                        text=""
                    )
                    row.template_search(
                        active_obj, "active_material",
                        context.blend_data, "materials")

                else:
                    row.template_ID(
                        active_obj,
                        "active_material",
                    )
                    row.prop_search(
                        active_obj, "active_material",
                        context.blend_data, "materials",
                        text=" ")

        ocol.label(text="Show:")
        y_scale_1 = 0.8
        row = ocol.row(align=True)
        row.scale_y = y_scale_1
        row.prop(
            context.object,
            'show_name',
            text="Name",
            toggle=True
        )
        row.prop(
            context.object,
            "show_wire",
            text="Wires",
            toggle=True
        )
        row.prop(
            context.object,
            "show_in_front",
            text="Clip",
            toggle=True,
            invert_checkbox=True
        )
        row.prop(
            context.object,
            "show_axis",
            text="Axis",
            toggle=True
        )

        row = ocol.row(align=True)
        row.scale_y = y_scale_1
        row.prop(
            context.object,
            'show_bounds',
            text="Bounds",
            toggle=True,
        )
        row.prop(
            context.object,
            'display_bounds_type',
            text="",
        )

        row = ocol.row(align=True)
        row.scale_y = y_scale_1
        row.prop(
            context.object,
            'show_texture_space',
            text="Texture Space",
            toggle=True,
        )
        row.prop(
            context.object.display,
            'show_shadows',
            text="Shadows",
            toggle=True,
        )

        label_row = ocol.row(align=True)

        label_row.label(text="Vertex Groups")

        # Yoinked from properties_data_mesh.py

        group = active_obj.vertex_groups.active

        rows = 4
        if group:
            rows = 4

        # obj_collection = context.view_layer.objects

        row = ocol.row(align=True)

        row.template_list(
                        "MESH_UL_vgroups",
                        "",
                        active_obj,
                        "vertex_groups",
                        active_obj.vertex_groups,
                        "active_index",
                        rows=rows
                        )

        col = row.column(align=True)

        # TODO: Fix this horrific naming 

        sub_row = col.row(align=True)
        sub_row.menu("MESH_MT_vertex_group_context_menu", icon='PROPERTIES', text="")

        sub_col = col.column(align=True)

        sub_col.operator("object.vertex_group_add", icon='ADD', text="")

        sub_col = col.column(align=True)
        sub_col.active = (True if group else False)
        show_active = False

        props = sub_col.operator("object.vertex_group_remove", icon='REMOVE', text="")
        props.all_unlocked = props.all = False

        sub_col.operator(
            "object.vertex_group_move",
            icon='TRIA_UP',
            text=""
            ).direction = 'UP'
        sub_col.operator(
            "object.vertex_group_move",
            icon='TRIA_DOWN',
            text=""
            ).direction = 'DOWN'

        if (active_obj.vertex_groups and
            (active_obj.mode == 'EDIT' or
            (active_obj.mode == 'WEIGHT_PAINT' and 
            active_obj.type == 'MESH' and
            active_obj.data.use_paint_mask_vertex))):
            show_active = True

        ocol.separator(factor=0.5)
        row = ocol.row(align=True)
        row.active = show_active

        row_width_check = check_width('UI', 9, 1, 440)

        label_tog = 0
        if not row_width_check[0]:
            label_tog = 1

        row_labels = [
                    ("Assign", " "),
                    ("Remove", " "),
                    ("Select", " "),
                    ("Deselect", " "),]

        row_icons = [
                    ('NONE', 'ADD'),
                    ('NONE', 'REMOVE'),
                    ('NONE', 'RESTRICT_SELECT_OFF'),
                    ('NONE', 'RESTRICT_SELECT_ON'),]

        sub = row.row(align=True)

        sub.operator(
                    "object.vertex_group_assign",
                    text=row_labels[0][label_tog],
                    icon=row_icons[0][label_tog]
                    )
        sub.operator(
                    "object.vertex_group_remove_from",
                    text=row_labels[1][label_tog],
                    icon=row_icons[1][label_tog]
                    )

        sub = row.row(align=True)

        sub.operator(
                    "object.vertex_group_select",
                    text=row_labels[2][label_tog],
                    icon=row_icons[2][label_tog]
                    )
        sub.operator(
                    "object.vertex_group_deselect",
                    text=row_labels[3][label_tog],
                    icon=row_icons[3][label_tog]
                    )

        row = ocol.row(align=True)
        row.active = show_active

        row.prop(context.tool_settings, "vertex_group_weight", text="Weight")

        row = ocol.row(align=True)
        row.label(text="Parent")

        # Parenting Info
        row = ocol.split(factor=0.65, align=True)
        row.prop(active_obj, 'parent', text="")

        subrow = row.row(align=True)

        subrow.prop(active_obj, 'parent_type', text="")
        subrow.prop(WLT_props, 'mp_active_subsections', index=1, text="", icon='DOWNARROW_HLT')

        if active_obj and active_obj.parent:
            if  WLT_props.mp_active_subsections[1]:

                section = ocol.column(align=True)

                row = section.row(align=True)

                row.operator("object.select_more", text="Family")
                row.operator("object.select_grouped", text="Siblings").type = 'SIBLINGS'

                row = section.column(align=True)

        ocol.label(text="Data")

        row = ocol.row(align=True)
        if active_obj is not None and active_obj.type == 'MESH':
            obj_data = active_obj.data
            # TODO: Verify that Blender has changed this
            # row.prop(obj_data, "use_customdata_edge_bevel", text="Store Bevel")
            # row.prop(obj_data, "use_customdata_edge_crease", text="Store Crease")

        ocol.label(text="Visibility")

        row_width_check = check_width('UI', 12, 1, 440)

        row_labels = [
                    ("Viewport", ""),
                    ("Render", ""),
                    ("Selection", ""),
                    ("Overlays", ""),
        ]

        label_tog = 0
        row_cols = 3
        if not row_width_check[0]:
            label_tog = 1

        row = ocol.grid_flow(columns=row_cols, align=True)

        row.prop(
            context.object,
            'hide_viewport',
            text=row_labels[0][label_tog],
            toggle=True,
        )
        row.prop(
            context.object,
            'hide_render',
            text=row_labels[1][label_tog],
            toggle=True,
        )
        row.prop(
            context.object,
            'hide_select',
            text=row_labels[2][label_tog],
            toggle=True,
        )

    elif active_obj and active_obj.type == 'CURVE':
        curve = active_obj.data
        act_spline = curve.splines.active

        if act_spline.type == 'BEZIER':

            active_point = 0

            for cp in act_spline.bezier_points:
                if cp.select_control_point:
                    active_point = cp

            if active_point:
                ocol.label(text="Active Point:")

                row = ocol.row(align=True)
                col = row.column(align=True)

                col.prop(
                    active_point,
                    'radius')

            if active_point:
                col = row.column(align=True)
                col.prop(
                    active_point,
                    'tilt')

        ocol.label(text="Curve Geometry:")

        row = ocol.row(align=True)
        col = row.column(align=True)

        col.prop(
            context.object.data,
            'resolution_u',
            text="U Resolution",
        )
        col.prop(
            context.object.data,
            'offset',
            text="Offset",
        )
        col.prop(
            context.object.data,
            'extrude',
            text="Extrude",
        )

        subrow = col.split(factor=0.65, align=True)
        subrow.prop(
            context.object.data,
            'twist_smooth',
            text="Smooth",
        )
        subrow.prop(
            context.object.data,
            'twist_mode',
            text="",
        )

        subrow = col.split(factor=0.65, align=True)
        subrow.prop(
            context.object.data,
            'taper_object',
            text="",
        )
        subrow.prop(
            context.object.data,
            'use_map_taper',
            text="Map Taper",
            toggle=True
        )

        ocol.label(text="Bevel")

        row = ocol.row(align=True)
        col = row.column(align=True)

        col.prop(
            context.object.data,
            'bevel_depth',
            text="Bevel Depth",
        )
        col.prop(
            context.object.data,
            'bevel_resolution',
            text="Bevel Segments",
        )

        subrow = col.split(factor=0.65, align=True)
        subrow.prop(
            context.object.data,
            'bevel_factor_start',
            text="Bevel Start",
        )
        subrow.prop(
            context.object.data,
            'bevel_factor_mapping_start',
            text="",
        )

        subrow = col.split(factor=0.65, align=True)
        subrow.prop(
            context.object.data,
            'bevel_factor_end',
            text="Bevel End",
            expand=True
        )
        subrow.prop(
            context.object.data,
            'bevel_factor_mapping_end',
            text="",
        )

        subrow = col.split(factor=0.65, align=True)
        subrow.prop(
            context.object.data,
            'bevel_object',
            text="",
        )
        subrow.prop(
            context.object.data,
            'use_fill_caps',
            text="Fill Caps",
            toggle=True
        )

        ocol.label(text="Spline Settings")

        row = ocol.row(align=True)
        col = row.column(align=True)
        col.alignment = 'EXPAND'

        subrow = col.row(align=True)
        subrow.prop(
            context.object.data,
            'fill_mode',
            text="Fill",
        )

        col.prop(
            act_spline,
            'tilt_interpolation',
            text="Tilt",
        )
        col.prop(
            act_spline,
            'radius_interpolation',
            text="Radius",
        )

        ocol.separator()

        row = ocol.row(align=True)
        row.scale_y = 0.75

        row.prop(
            act_spline,
            'use_cyclic_u',
            text="Cyclic",
            toggle=True,
        )
        row.prop(
            act_spline,
            'use_smooth',
            text="Smooth",
            toggle=True,
        )
        row.prop(
            context.object.data,
            'use_radius',
            text="Radius",
            toggle=True,
        )
        row.prop(
            context.object.data,
            'use_stretch',
            text="Stretch",
            toggle=True,
        )

        row = ocol.row(align=True)
        row.scale_y = 0.75

        row.prop(
            context.object.data,
            'use_deform_bounds',
            text="Clamp Bounds",
            toggle=True,
        )
        row.prop(
            context.object.data,
            'use_fill_deform',
            text="Fill Deformed",
            toggle=True,
        )

    elif active_obj and active_obj.type == 'LATTICE':
        ocol.label(text="Resolution:")

        row = ocol.row(align=True)
        row.prop(
            active_obj.data,
            'points_u')
        row.prop(
            active_obj.data,
            'interpolation_type_u',
            text="")

        row = ocol.row(align=True)
        row.prop(
            active_obj.data,
            'points_v')
        row.prop(
            active_obj.data,
            'interpolation_type_v',
            text="")

        row = ocol.row(align=True)
        row.prop(
            active_obj.data,
            'points_w')
        row.prop(
            active_obj.data,
            'interpolation_type_w',
            text="")

        ocol.separator()

        label_row = ocol.row(align=True)

        label_row.label(text="Vertex Groups")

        # Yoinked from properties_data_mesh.py

        group = active_obj.vertex_groups.active

        rows = 4
        if group:
            rows = 4

        # obj_collection = context.view_layer.objects

        row = ocol.row(align=True)

        row.template_list(
                        "MESH_UL_vgroups",
                        "",
                        active_obj,
                        "vertex_groups",
                        active_obj.vertex_groups,
                        "active_index",
                        rows=rows
                        )

        col = row.column(align=True)
        sub_row = col.row(align=True)
        sub_row.menu("MESH_MT_vertex_group_context_menu", icon='PROPERTIES', text="")

        sub_col = col.column(align=True)

        sub_col.operator("object.vertex_group_add", icon='ADD', text="")

        sub_col = col.column(align=True)
        sub_col.active = (True if group else False)
        show_active = False

        props = sub_col.operator("object.vertex_group_remove", icon='REMOVE', text="")
        props.all_unlocked = props.all = False

        sub_col.operator(
            "object.vertex_group_move",
            icon='TRIA_UP',
            text=""
            ).direction = 'UP'
        sub_col.operator(
            "object.vertex_group_move",
            icon='TRIA_DOWN',
            text=""
            ).direction = 'DOWN'

        do = False
        if (active_obj.vertex_groups and
            (active_obj.mode == 'EDIT' or
                (active_obj.mode == 'WEIGHT_PAINT'and
                    active_obj.type == 'MESH' and
                    active_obj.data.use_paint_mask_vertex))):
            do = True

        ocol.separator(factor=0.5)
        row = ocol.row(align=True)
        row.active = do

        row_width_check = check_width('UI', 9, 1, 440)

        label_tog = 0
        if not row_width_check[0]:
            label_tog = 1

        row_labels = [
                    ("Assign", " "),
                    ("Remove", " "),
                    ("Select", " "),
                    ("Deselect", " "),
        ]

        row_icons = [
                    ('NONE', 'ADD'),
                    ('NONE', 'REMOVE'),
                    ('NONE', 'RESTRICT_SELECT_OFF'),
                    ('NONE', 'RESTRICT_SELECT_ON'),
        ]

        sub = row.row(align=True)
        sub.operator(
                    "object.vertex_group_assign",
                    text=row_labels[0][label_tog],
                    icon=row_icons[0][label_tog]
                    )
        sub.operator(
                    "object.vertex_group_remove_from",
                    text=row_labels[1][label_tog],
                    icon=row_icons[1][label_tog]
                    )

        sub = row.row(align=True)
        sub.operator(
                    "object.vertex_group_select",
                    text=row_labels[2][label_tog],
                    icon=row_icons[2][label_tog]
                    )
        sub.operator(
                    "object.vertex_group_deselect",
                    text=row_labels[3][label_tog],
                    icon=row_icons[3][label_tog]
                    )

        row = ocol.row(align=True)
        row.active = show_active

        row.prop(context.tool_settings, "vertex_group_weight", text="Weight")

        ocol.separator()
        row = ocol.row(align=True)
        row.prop(active_obj.data, "use_outside")

    elif active_obj and active_obj.type == 'EMPTY':
        ocol.label(text="Show:")
        row = ocol.row(align=True)
        row.prop(
            context.object,
            'empty_display_type',
            text="",
            expand=False
        )
        row.prop(
            context.object,
            'parent',
            text="",
        )

        row = ocol.split(factor=0.5, align=True)
        row.prop(
            context.object,
            'empty_display_size',
            text="",
            expand=False
        )

        row_inner = row.row(align=True)

        row_inner.prop(
            context.object,
            'show_name',
            text="Name",
            toggle=True
        )
        row_inner.prop(
            context.object,
            'show_axis',
            text="Axis",
            toggle=True
        )

        if active_obj.empty_display_type == 'IMAGE':
            row = ocol.split(factor=0.5, align=True)
            row.prop(
                context.object,
                'use_empty_image_alpha',
                text="Use Alpha",
                toggle=True
            )
            row.prop(
                context.object,
                'color',
                text="",
                index=3,
                slider=True
            )

            col = ocol.column(align=True)
            col.template_ID_preview(
                            context.object,
                            "data",
                            open="image.open",
                            unlink="object.unlink_data",
                            hide_buttons=False
                            )

            ocol.separator(factor=2)

            col = ocol.column(align=True)
            col.template_image(
                                context.object,
                                "data",
                                context.object.image_user,
                                compact=True,
                                )

            row = ocol.row(align=True)

            sub = row.column(align=True)

            sub.label(text="Offset:")

            sub.prop(context.object, "empty_image_offset", text="X", index=0)
            sub.prop(context.object, "empty_image_offset", text="Y", index=1)

            row = ocol.split(factor=0.5, align=True)
            sub = row.column(align=True)

            sub.label(text="Depth:")
            sub.prop(context.object, "empty_image_depth", text="", expand=False)

            sub = row.column(align=True)
            sub.label(text="Side:")
            sub.prop(context.object, "empty_image_side", text="", expand=False)

            col = ocol.column(align=True)
            col.label(text="Options")
            col.prop(
                    context.object,
                    "show_empty_image_orthographic",
                    text="Display Orthographic"
                    )
            col.prop(
                    context.object,
                    "show_empty_image_perspective",
                    text="Display Perspective"
                    )
            col.prop(context.object, "show_empty_image_only_axis_aligned")

    elif active_obj and active_obj.type == 'CAMERA':

        ocol.label(text="Show:")

        row = ocol.row(align=True)
        row.prop(
            context.object.data,
            'show_limits',
            text="Limits",
            toggle=True
        )
        row.prop(
            context.object.data,
            'show_mist',
            text="Mist",
            toggle=True
        )
        row.prop(
            context.object.data,
            'show_sensor',
            text="Sensor",
            toggle=True
        )
        row.prop(
            context.object.data,
            'show_name',
            text="Name",
            toggle=True
        )

        row = ocol.row(align=True)
        row.prop(
            context.object.data,
            'display_size',
            text="Display Size",
        )

        ocol.label(text="Settings:")

        col = ocol.column(align=True)

        sub = col.row(align=True)

        if context.object.data.sensor_fit == 'AUTO':
            sub.prop(
                context.object.data,
                'sensor_width',
                text="Sensor Size",
            )
        elif context.object.data.sensor_fit == 'HORIZONTAL':
            sub.prop(
                context.object.data,
                'sensor_width',
                text="Sensor Width",
            )
        elif context.object.data.sensor_fit == 'VERTICAL':
            sub.prop(
                context.object.data,
                'sensor_height',
                text="Sensor Height",
            )

        op = sub.operator(
            "wm.context_cycle_enum",
            text="",
            icon='CON_SIZELIKE'
        )
        op.data_path = "object.data.sensor_fit"
        op.wrap = True

        sub = col.row(align=True)

        if context.object.data.lens_unit == 'MILLIMETERS':
            sub.prop(
                context.object.data,
                'lens',
            )
        else:
            sub.prop(
                context.object.data,
                'angle',
            )

        op = sub.operator(
            "wm.context_toggle_enum",
            text="",
            icon='OUTLINER_OB_CAMERA'
        )
        op.data_path = "object.data.lens_unit"
        op.value_1 = 'FOV'
        op.value_2 = 'MILLIMETERS'

        col = ocol.column(align=True)
        sub = col.row(align=True)

        sub.prop(
            context.object.data,
            'clip_start'
        )

        sub.prop(
            context.object.data,
            'clip_end'
        )

        ocol.label(text="Stuffs:")

        col = ocol.column(align=True)
        sub = col.row(align=True)

        sub.prop(
            context.space_data,
            'lock_camera',
            toggle=True
        )

        sub = col.row(align=True)
        sub.prop(
            context.object.data,
            'show_passepartout',
            text="Dim Outer",
            toggle=True
        )
        sub.prop(
            context.object.data,
            'passepartout_alpha',
            text="",
        )

        col = ocol.column(align=True)
        col.scale_y = 0.75
        col.prop(
            context.object,
            'location',
        )

        ocol.label(text="Overlays:")

        col = ocol.column(align=True)
        sub = col.row(align=True)

        sub.prop(
            context.object.data,
            'show_composition_thirds',
            text="Thirds",
            toggle=True
        )
        sub.prop(
            context.object.data,
            'show_composition_center',
            text="Center",
            toggle=True
        )
        sub.prop(
            context.object.data,
            'show_composition_golden',
            text="Phi",
            toggle=True
        )

        # RETURN HERE

        ocol.label(text="Scene Cameras:")

        for cam in bpy.data.cameras:
            if cam.users > 0:
                row = ocol.row(align=True)
                row.prop(
                    cam,
                    "name",
                    text=""
                    )

                if context.scene.camera and context.scene.camera.name == cam.name:
                    icon = 'OUTLINER_OB_CAMERA'
                else:
                    icon = 'OUTLINER_DATA_CAMERA'

                op = row.operator(
                    "wm.context_set_id",
                    text="",
                    icon=icon
                )
                op.data_path = "scene.camera"
                op.value = str(cam.name)

                op = row.operator(
                    "wlt.zoop",
                    text="",
                    icon='LIGHT'
                )
                op.target_camera = str(cam.name)

    elif active_obj and active_obj.type == 'LIGHT':
        ocol.label(text="Show:")
        row = ocol.row(align=True)
        row.prop(
            context.object,
            'show_name',
            text="Name",
            toggle=True
        )
        row.prop(
            context.object,
            "show_in_front",
            text="Clip",
            toggle=True,
            invert_checkbox=True
        )
        row.prop(
            context.object,
            "show_axis",
            text="Axis",
            toggle=True
        )

        ocol.label(text="Settings")

        row = ocol.row(align=True)

        row.prop(context.object.data, "type", expand=True)

        row = ocol.split(factor=0.75, align=True)

        row.prop(context.object.data, "energy", expand=False)
        row.prop(context.object.data, "color", text="", expand=False)

        row = ocol.row(align=True)
        row.prop(context.object.data, "specular_factor", text="Specular", expand=False)

        if context.object.data.type == 'POINT' or context.object.data.type == 'SPOT':
            row.prop(context.object.data, "shadow_soft_size", text="Radius", expand=False)
        elif context.object.data.type == 'SUN':
            row.prop(context.object.data, "angle", text="Angle", expand=False)
        elif context.object.data.type == 'AREA':
            row.prop(context.object.data, "shape", text="", expand=False)

        if context.object.data.type == 'SPOT':
            ocol.separator()

            row = ocol.split(align=True)

            sub = row.row(align=True)

            sub.prop(context.object.data, "show_cone", text="", icon='LIGHT_SPOT')
            sub.prop(context.object.data, "spot_size", text="Size", expand=False)

            sub = row.row(align=True)

            sub.prop(context.object.data, "spot_blend", text="Blend", expand=False)
        elif context.object.data.type == 'AREA':
            ocol.separator()

            row = ocol.row(align=True)

            row.prop(context.object.data, "size", text="X", expand=False)
            if not context.object.data.shape == 'DISK':
                row.prop(context.object.data, "size_y", text="Y", expand=False)

        ocol.label(text="Shadows")

        row = ocol.row(align=True)

        col = row.column(align=True)

        col.scale_y = 2
        col.prop(
                context.object.data,
                "use_shadow",
                text="",
                icon='OUTLINER_DATA_LIGHTPROBE'
                )

        col = row.column(align=True)
        col.active = context.object.data.use_shadow

        col.prop(
                context.object.data,
                "shadow_buffer_clip_start",
                text="Clip Start",
                )

        col.prop(
                context.object.data,
                "shadow_buffer_bias",
                text="Bias",
                )

        ocol.label(text="Contact Shadows")

        row = ocol.row(align=True)

        col = row.column(align=True)

        col.active = context.object.data.use_shadow

        col.scale_y = 3

        col.prop(
                context.object.data,
                "use_contact_shadow",
                text="",
                icon='MOD_PHYSICS'
                )

        col = row.column(align=True)

        col.active = (
            context.object.data.use_shadow
            and context.object.data.use_contact_shadow)

        col.prop(
                context.object.data,
                "contact_shadow_distance",
                text="Distance",
                )

        col.prop(
                context.object.data,
                "contact_shadow_bias",
                text="Bias",
                )

        col.prop(
                context.object.data,
                "contact_shadow_thickness",
                text="Thickness",
                )

        ocol.label(text="Custom Distance")

        row = ocol.row(align=True)

        col = row.column(align=True)

        col.prop(
                context.object.data,
                "use_custom_distance",
                text="",
                icon='DRIVER_DISTANCE'
                )

        col = row.column(align=True)

        col.active = context.object.data.use_custom_distance

        col.prop(
                context.object.data,
                "cutoff_distance",
                text="Distance",
                )

        ocol.label(text="What?")

        row = ocol.row(align=True)

        col = row.column(align=True)

        col.prop(
                context.object.data,
                "shadow_color",
                )
        col.prop(
                context.object.data,
                "falloff_type",
                )
        col.prop(
                context.object.data,
                "quadratic_attenuation",
                )
        col.prop(
                context.object.data,
                "constant_coefficient",
                )



    elif active_obj and active_obj.type == 'LIGHT_PROBE':
        probe = context.object.data
        ocol.label(text="Settings")

        if probe.type == 'GRID':
            row = ocol.row(align=True)
            row.prop(
                    probe,
                    "intensity",
                    text="Intensity",
                    )
            row.prop(
                    probe,
                    "falloff",
                    text="Falloff",
                    )

            row = ocol.row(align=True)

            row.prop(
                    probe,
                    "influence_distance",
                    text="Distance",
                    )

            row = ocol.row(align=True)
            row.prop(
                    probe,
                    "clip_start",
                    text="Clip Start",
                    )

            row = ocol.row(align=True)
            row.prop(
                    probe,
                    "clip_end",
                    text="Clip End",
                    )

            ocol.label(text="Resolution:")

            row = ocol.row(align=True)

            row.prop(
                    probe,
                    "grid_resolution_x",
                    text="X:",
                    )
            row.prop(
                    probe,
                    "grid_resolution_x",
                    text="Y:",
                    )
            row.prop(
                    probe,
                    "grid_resolution_x",
                    text="Z:",
                    )
        elif probe.type == 'PLANAR':
            row = ocol.row(align=True)

            row.prop(
                    probe,
                    "falloff",
                    text="Falloff",
                    )
            row.prop(
                    probe,
                    "influence_distance",
                    text="Distance",
                    )

            row = ocol.row(align=True)

            row.prop(
                    probe,
                    "clip_start",
                    text="Offset",
                    )
        else:
            row = ocol.row(align=True)

            row.prop(
                    probe,
                    "intensity",
                    text="Intensity",
                    )
            row.prop(
                    probe,
                    "falloff",
                    text="Falloff",
                    )
            row = ocol.row(align=True)

            row.prop(
                    probe,
                    "influence_distance",
                    text="Distance",
                    )

            row = ocol.row(align=True)

            row.prop(
                    probe,
                    "clip_start",
                    text="Clip Start",
                    )

            row = ocol.row(align=True)

            row.prop(
                    probe,
                    "clip_end",
                    text="Clip End",
                    )

            row = ocol.row(align=True)
            row.label(text="Custom Paralax")

            row = ocol.row(align=True)

            col = row.column(align=True)
            col.scale_y = 2

            ico = 'OUTLINER_DATA_LIGHTPROBE'
            if probe.use_custom_parallax:
                ico = 'OUTLINER_OB_LIGHTPROBE'

            col.prop(
                    probe,
                    "use_custom_parallax",
                    text="",
                    icon=ico
                    )

            col = row.column(align=True)
            col.active = probe.use_custom_parallax
            col.prop(
                    probe,
                    "parallax_type",
                    text="",
                    )
            col.prop(
                    probe,
                    "parallax_distance",
                    text="Radius",
                    )
        ocol.label(text="Visibility:")

        row = ocol.row(align=True)
        row.prop(
                probe,
                "visibility_collection",
                text=""
                )
        row.prop(probe, "invert_visibility_collection", text="", icon='ARROW_LEFTRIGHT')

        if probe.type == 'GRID':
            row = ocol.row(align=True)

            row.prop(
                    probe,
                    "visibility_buffer_bias",
                    text="Bias"
                    )
            row.prop(
                    probe,
                    "visibility_bleed_bias",
                    text="Bleed"
                    )
            row = ocol.row(align=True)
            row.prop(
                    probe,
                    "visibility_blur",
                    text="Blur"
                    )

        ocol.label(text="Display:")

        col = ocol.column_flow(columns=1, align=True)
        col.alignment = 'LEFT'
        ico = ('CHECKBOX_HLT' if probe.show_influence else 'CHECKBOX_DEHLT')
        col.prop(
                probe,
                "show_influence",
                text="Influence",
                toggle=True,
                emboss=False,
                icon=ico
                )
        ico = ('CHECKBOX_HLT' if probe.show_clip else 'CHECKBOX_DEHLT')
        col.prop(
                probe,
                "show_clip",
                text="Clipping",
                toggle=True,
                emboss=False,
                icon=ico
                )
        if not (probe.type in {'PLANAR', 'GRID'}):
            ico = ('CHECKBOX_HLT' if probe.show_parallax else 'CHECKBOX_DEHLT')
            col.prop(
                    probe,
                    "show_parallax",
                    text="Parallax",
                    toggle=True,
                    emboss=False,
                    icon=ico
                    )

    if active_obj and active_obj.field:
        field = active_obj.field

        dep = (True if not active_obj.field.type == 'NONE' else False)

        bcol.label(text="Physics:")

        row = bcol.row(align=True)

        row.operator(
                    "object.forcefield_toggle",
                    text="Force Field",
                    icon='FORCE_FORCE',
                    depress=dep
                    )

        row.prop(field, "type", text="")

        if field.type == 'NONE':
            pass

        elif field.type == 'GUIDE':
            col = bcol.column(align=True)

            col.prop(field, "guide_minimum")
            col.prop(field, "guide_free")
            col.prop(field, "falloff_power")
            col.prop(field, "use_guide_path_add")
            col.prop(field, "use_guide_path_weight")

            col = bcol.column(align=True)
            col.prop(field, "guide_clump_amount", text="Clumping amount")
            col.prop(field, "guide_clump_shape")
            col.prop(field, "use_max_distance")

            sub = col.column(align=True)
            sub.active = field.use_max_distance
            sub.prop(field, "distance_max")

        elif field.type == 'TEXTURE':
            col = bcol.column(align=True)
            col.prop(field, "texture_mode")

            col.separator()

            col.prop(field, "strength")

            col = bcol.column(align=True)
            col.prop(field, "texture_nabla")
            col.prop(field, "use_object_coords")
            col.prop(field, "use_2d_force")

        elif field.type == 'SMOKE_FLOW':
            col = bcol.column(align=True)
            col.prop(field, "strength")
            col.prop(field, "flow")

            col = bcol.column(align=True)
            col.prop(field, "source_object")
            col.prop(field, "use_smoke_density")
        else:
            col = bcol.column(align=True)
            if field.type == 'DRAG':
                col.prop(field, "linear_drag", text="Linear")
            else:
                col.prop(field, "strength")

            if field.type == 'TURBULENCE':
                col.prop(field, "size")
                col.prop(field, "flow")

            elif field.type == 'HARMONIC':
                col.prop(field, "harmonic_damping", text="Damping")
                col.prop(field, "rest_length")

            elif field.type == 'VORTEX' and field.shape != 'POINT':
                col.prop(field, "inflow")

            elif field.type == 'DRAG':
                col.prop(field, "quadratic_drag", text="Quadratic")

            else:
                col.prop(field, "flow")

            col.prop(field, "apply_to_location", text="Affect Location")
            col.prop(field, "apply_to_rotation", text="Affect Rotation")

            col = bcol.column(align=True)
            sub = col.column(align=True)
            sub.prop(field, "noise", text="Noise Amount")
            sub.prop(field, "seed", text="Seed")

            if field.type == 'TURBULENCE':
                col.prop(field, "use_global_coords", text="Global")

            elif field.type == 'HARMONIC':
                col.prop(field, "use_multiple_springs")

            if field.type == 'FORCE':
                col.prop(field, "use_gravity_falloff", text="Gravitation")

            col.prop(field, "use_absorption")

def cursor_tab(layout, context):
    active_obj = context.view_layer.objects.active
    wm = bpy.context.window_manager
    WLT_props = context.workspace.WLT

    if not WLT_props.mp_tabs:
        WLT_props.mp_tabs = '0'

    # Aliased Stuff
    scene = context.scene
    cursor = scene.cursor
    tool_settings = context.scene.tool_settings

    units = scene.unit_settings
    overlay = context.space_data.overlay
    v3dtheme = context.preferences.themes[0].view_3d

    main_col = layout

    row = main_col.row(align=True)

    row.operator(
        "wlt.align_cursor_to_orientation",
        text="To Transform",
    )

    row.operator(
        "view3d.snap_cursor_to_center",
        text="To Center",
    )

    row = main_col.row(align=True)

    op = row.operator(
        "wlt.snap_align_cursor",
        text="Align",)
    op.move_mode = 'ALIGN_ONLY'

    op = row.operator(
        "wlt.snap_align_cursor",
        text="Snap",)
    op.move_mode = 'SNAP_ONLY'

    # main_col.separator()

    main_col.prop(cursor, "location")

    if cursor.rotation_mode == 'QUATERNION':
        main_col.prop(cursor, "rotation_quaternion")
    elif cursor.rotation_mode == 'AXIS_ANGLE':
        main_col.prop(cursor, "rotation_axis_angle")
    else:
        main_col.prop(cursor, "rotation_euler")

    main_col.separator()

    label_row = main_col.row(align=True)
    label_row.emboss = 'NONE'
    label_row.label(text="Here be Dragons")
    op = label_row.operator(
        "wlt.tool_tip",
        text="",
        icon='INFO'
    )
    op.tooltip = "The stuff you see here is experimental/debug stuff. It might explode."

    main_col.prop(
        context.workspace.WLT,
        'vp_orbit_target',
        text=""
    )

    main_col.separator()

    WLT_prefs = get_prefs()
    items = WLT_prefs.keymap_group_filter.split(', ')

    if len(items) > 2:
        for item in items:
            main_col.prop_enum(
                context.workspace.WLT,
                "group_filter_enum",
                value=item,
                text=item
            )

# Yes, we have ourselves a function array.
tab_array = [transform_tab, camera_tab, shading_tab, active_obj_tab, cursor_tab]

class VIEW3D_PT_meta_panel(Panel):
    bl_idname = "VIEW3D_PT_meta_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "WLT"
    bl_label = "Meta Panel"
    bl_options = { 'HEADER_LAYOUT_EXPAND',  }

    bl_ui_units_x = 12

    @classmethod
    def poll(cls, context):
        if context.view_layer.objects.active:
            return True

    @staticmethod
    def _active_context_member(context):
        obj = context.object
        if obj:
            object_mode = obj.mode
            if object_mode == 'POSE':
                return "active_pose_bone"
            elif object_mode == 'EDIT' and obj.type == 'ARMATURE':
                return "active_bone"
            else:
                return "object"
        return ""

    @classmethod
    def transform_poll(cls, context):
        import rna_prop_ui
        member = cls._active_context_member(context)

        if member:
            context_member, member = rna_prop_ui.rna_idprop_context_value(context, member, object)
            return context_member and rna_prop_ui.rna_idprop_has_properties(context_member)

        return False

    @classmethod
    def get_shading(cls, context):
        view = context.space_data
        if view.type == 'VIEW_3D':
            return view.shading
        else:
            return context.scene.display.shading

    def draw(self, context):
        WLT_props = context.workspace.WLT

        if not WLT_props.mp_tabs:
            WLT_props.mp_tabs = '0'

        # Aliased Stuff
        scene = context.scene
        layout = self.layout
        root = layout.column(align=True)
        tb_width_check = check_width('UI', 12, 1, 440)

        tab_labels = [
                    ("Transforms", ""),
                    ("Cameras", ""),
                    ("Shading", ""),
                    ("Active", ""),
                    ("Cursor", "")
        ]

        tb_ico_only = 0
        if not tb_width_check[0]:
            tb_ico_only = 1

        tb_row = root.row(align=True)
        tb_row.alignment = 'RIGHT'

        for i, item in enumerate(WLT_props.bl_rna.properties['mp_tabs'].enum_items):
            tb_row.prop_enum(
                WLT_props,
                'mp_tabs',
                str(i),
                text=tab_labels[i][tb_ico_only]
            )

        rbox = root.box()
        bcol = rbox.column(align=True)

        # Tab names are just numbers, so we can call by index from the array.
        tab_array[int(WLT_props.mp_tabs)](bcol, context)

        footer_row = root.row(align=True)

        footer_row.scale_y = 1
        footer_row.prop(
            WLT_props,
            "mp_debug",
            text="Debug",
            icon='TOOL_SETTINGS',
            index=0,
            toggle=True
            )
        footer_row.prop(
            WLT_props,
            "mp_debug",
            text="",
            icon='KEYFRAME_HLT',
            index=1,
            toggle=True
            )
        footer_row.prop(
            WLT_props,
            "mp_debug",
            text="",
            icon='LAYER_USED',
            index=2,
            toggle=True
            )
        footer_row.prop(
            WLT_props,
            "mp_debug",
            text="",
            icon='DOT',
            index=3,
            toggle=True
            )


class VIEW3D_MT_set_origin(bpy.types.Menu):
    bl_label = "WLT Set Origin"

    def draw(self, context):
        layout = self.layout

        op = layout.operator(
            "wlt.origin_to_bbox",
            text='Origin to Front Left',
        )
        op.box_mode = 'POINT'
        op.box_point = 'XNEG_YPOS_ZNEG'

        op = layout.operator(
            "wlt.origin_to_bbox",
            text='Origin to Front Right',
        )
        op.box_mode = 'POINT'
        op.box_point = 'XPOS_YPOS_ZNEG'

        op = layout.operator(
            "wlt.origin_to_bbox",
            text='Origin to Back Left',
        )
        op.box_mode = 'POINT'
        op.box_point = 'XNEG_YNEG_ZNEG'

        op = layout.operator(
            "wlt.origin_to_bbox",
            text='Origin to Back Right',
        )
        op.box_mode = 'POINT'
        op.box_point = 'XPOS_YNEG_ZNEG'

        op = layout.operator(
            "wlt.origin_to_bbox",
            text='Origin to Bottom',
        )
        op.box_mode = 'FACE'
        op.box_face = 'ZNEG'

        op = layout.operator(
            "wlt.origin_to_bbox",
            text='Origin to Center',
        )
        op.box_mode = 'FACE'
        op.box_face = 'CENTER'

        op = layout.operator(
            "wlt.set_origin",
            text='Origin to Selected',
        )
        op.snap_mode = 'SELECTION'

        op = layout.operator(
            "wlt.set_origin",
            text='Origin to Cursor',
        )
        op.snap_mode = 'CURSOR'

OUT = [
    VIEW3D_PT_meta_panel,
    CUSTOM_UL_camera_list,
    VIEW3D_MT_set_origin,
]