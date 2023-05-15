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
from bpy.types import PropertyGroup
from mathutils import Matrix
from bpy.props import (
    EnumProperty,
    FloatVectorProperty,
    BoolProperty,
    BoolVectorProperty,
    IntProperty,
    IntVectorProperty,
    StringProperty,
    PointerProperty,
    FloatProperty,
)

# Root Properties

class ModalProps(PropertyGroup):
    tablet_modal: BoolProperty(
                                name="Layout Toggle",
                                default=False
                             )

    edit_modal: BoolProperty(
                                name="Pivot Toggle",
                                default=False
                            )

    transform_modal: BoolProperty(
                                name="Snapping Toggle",
                                default=False
                           )

    mirror_modal: BoolProperty(
                                name="Mirror Modal",
                                default=False
                           )

    mm_use_cursor: BoolProperty(
                                name="Mirror Modal",
                                default=False
                           )

    mm_use_cursor_location: BoolProperty(
                                name="Mirror Modal",
                                default=False
                           )


# Fast Panel Stuff
class FastPanelProps(PropertyGroup):

    # Unused
    layout_bool: BoolProperty(
                                name="Layout Toggle",
                                default=False
                             )

    # Unused
    pivot_bool: BoolProperty(
                                name="Pivot Toggle",
                                default=False
                            )

    # Unused
    snap_bool: BoolProperty(
                                name="Snapping Toggle",
                                default=False
                           )

    snap_cycle_items = [
                    ('MIN', "Minimal", "Minimal", 'NONE', 1),
                    ('COMPACT', "Compact", "Compact", 'NONE', 2),
                    ('FULL', "Full", "Full", 'NONE', 3)
                 ]

    snap_cycle: EnumProperty(
        name=' ',
        description='Snap Section Layout',
        items=snap_cycle_items
    )

    fast_panel_tab_items = [
                ('MEASURES', "Measures", "Measurement Tools and Overlays", 'DESKTOP', 1),
                ('OVERLAYS', "Overlays", "Viewport Overlays", 'SEQ_STRIP_DUPLICATE', 2),
                ('NORMALS', "Normals", "Mesh Normal Overlays", 'SNAP_FACE_CENTER', 3),
                ('GIZMOS', "Gizmos", "Gizmo Options", 'CON_OBJECTSOLVER', 4),
                ('DISPLAY', "Display", "Object Display Options", 'RIGID_BODY_CONSTRAINT', 5)
                           ]

    fast_panel_tabs: EnumProperty(
        name=' ',
        description='Fast Panel Tab',
        items=fast_panel_tab_items
    )

class WLT_GizmoProperties(PropertyGroup):
    """
    Gizmo stuff. Most of this is old things that should be depreciated.
    Treat this property group as a holding cell.
    """

    context_pie_items = [
                ('VERTEX', "Vertex Mode", "", 'NONE', 1),
                ('EDGE', "Edge Mode", "", 'NONE', 2),
                ('FACE', "Face Mode", "", 'NONE', 3),
                ('SPECIAL', "Dynamic Mode", "", 'NONE', 4),
                    ]

    cxt_pie_mode: EnumProperty(
        items=context_pie_items,
        name="Context Pie Mode",
        default='VERTEX'
    )

    gizmo_pivot_mode_items = [
                ('ACTIVE', "Active", "", 'NONE', 1),
                ('ORIGIN', "Origin", "", 'NONE', 2),
                ('CURSOR', "3D Cursor", "", 'NONE', 3),
                ('MEDIAN', "Median Point", "", 'NONE', 4),
                    ]

    gizmo_pivot_mode: EnumProperty(
        items=gizmo_pivot_mode_items,
        name="Gizmo Pivot Mode",
        default='CURSOR'
    )

    show_pivot: BoolProperty(
        name="Show Pivot",
        default=False
    )

    gizmo_scale: FloatProperty(
        name="Gizmo Scale",
        min=1.0,
        max=4.0,
        step=0.1,
        default=1
    )

    gizmo_selector_items = [
                ('ACTIVE', "Active", "", 'NONE', 1),
                ('ORIGIN', "Origin", "", 'NONE', 2),
                ('CURSOR', "3D Cursor", "", 'NONE', 4),
                ('MEDIAN', "Median Point", "", 'NONE', 8),
                    ]

    gizmo_selector: EnumProperty(
        name="Gizmo Selector",
        description="",
        items=gizmo_selector_items,
        options={'ENUM_FLAG'},
        default=None
    )






class ObjectMatrixConversions(PropertyGroup):

    def set_float(self, value):
        import mathutils
        obj = bpy.context.view_layer.objects.active
        if obj:
            rot_in = mathutils.Euler(value)

            debug = False

            if debug:
                print(str(value))
                print(str(rot_in) + "\n")

            src_loc, _src_rot, _src_scale = obj.matrix_world.decompose()

            loc_mat = mathutils.Matrix.Translation(src_loc)
            rot_mat = rot_in.to_matrix()

            full_mat = loc_mat @ rot_mat.to_4x4()

            obj.matrix_world = full_mat
        else:
            self["prop"] = value

    # Local Space Getters
    def get_local_translation(self):
        obj = bpy.context.view_layer.objects.active
        if obj:
            loc, _rot, _scale = obj.matrix_local.decompose()
            return loc.to_tuple()
        else:
            return (0, 0, 0)

    def get_local_rotation(self):
        obj = bpy.context.view_layer.objects.active
        if obj:
            _loc, rot, _scale = obj.matrix_local.decompose()
            eul_rot = rot.to_euler()
            rot_tup = (eul_rot.x, eul_rot.y, eul_rot.z)
            return rot_tup
        else:
            return (0, 0, 0)

    def get_local_scale(self, context):
        obj = context.view_layer.objects.active
        if obj:
            _loc, _rot, scale = obj.matrix_local.decompose()
            return scale.to_tuple()
        else:
            return (0, 0, 0)

    # World Space Getters
    def get_world_translation(self):
        obj = bpy.context.view_layer.objects.active
        if obj:
            loc, _rot, _scale = obj.matrix_world.decompose()
            return loc.to_tuple()
        else:
            return (0, 0, 0)

    def get_world_rotation(self):
        obj = bpy.context.view_layer.objects.active
        if obj:
            eul_rot = obj.rotation_euler
            rot = obj.matrix_world.to_euler('XYZ', eul_rot)

            debug = False

            if debug:
                print(str(rot))

            return rot
        else:
            return (0, 0, 0)

    def get_world_scale(self, context):
        obj = context.view_layer.objects.active
        if obj:
            _loc, _rot, scale = obj.matrix_world.decompose()
            return scale.to_tuple()
        else:
            return (0, 0, 0)

    local_loc: FloatVectorProperty(
                                name="Object Local Location",
                                description="Object Local Location",
                                default=(0.0, 0.0, 0.0),
                                subtype='TRANSLATION',
                                get=get_local_translation
                                )

    local_rot: FloatVectorProperty(
                                name="Object Local Rotation",
                                description="Object Local Rotation",
                                default=(0.0, 0.0, 0.0),
                                subtype='EULER',
                                get=get_local_rotation
                                )

    world_loc: FloatVectorProperty(
                                name="Object World Location",
                                description="Object World Location",
                                default=(0.0, 0.0, 0.0),
                                subtype='TRANSLATION',
                                get=get_world_translation
                                )

    world_rot: FloatVectorProperty(
                                name="Object World Rotation",
                                description="Object World Rotation",
                                default=(0.0, 0.0, 0.0),
                                subtype='EULER',
                                get=get_world_rotation,
                                set=set_float
                                )


class CustomTransforms(PropertyGroup):

    def get_matrix(self, value):
        return 0

    transformA: FloatVectorProperty(
        name='',
        description='A persistent custom transform orientation',
        subtype='MATRIX',
        size=9,
        default=[b for a in Matrix.Identity(4).to_3x3() for b in a]
    )

    transformB: FloatVectorProperty(
        name='',
        description='A persistent custom transform orientation',
        subtype='MATRIX',
        size=9,
        default=[b for a in Matrix.Identity(4).to_3x3() for b in a]
    )

    transformC: FloatVectorProperty(
        name='',
        description='A persistent custom transform orientation',
        subtype='MATRIX',
        size=9,
        default=[b for a in Matrix.Identity(4).to_3x3() for b in a]
    )

    transformD: FloatVectorProperty(
        name='',
        description='A persistent custom transform orientation',
        subtype='MATRIX',
        size=9,
        default=[b for a in Matrix.Identity(4).to_3x3() for b in a]
    )

    transformE: FloatVectorProperty(
        name='',
        description='A persistent custom transform orientation',
        subtype='MATRIX',
  
        size=9,
        default=[b for a in Matrix.Identity(4).to_3x3() for b in a]
    )

    transformF: FloatVectorProperty(
        name='',
        description='A persistent custom transform orientation',
        subtype='MATRIX',
        size=9,
        default=[b for a in Matrix.Identity(4).to_3x3() for b in a]
    )



def metapanel_layout_items():
    items = [
        ('0', "Move", "Transformation Tab", 'OBJECT_ORIGIN', 1),
        ('1', "Tools", "Camera Manager Tab", 'OUTLINER_DATA_CAMERA', 2),
        ('2', "Draw", "Viewport Overlays", 'SHADING_RENDERED', 3),
        ('3', "Active", "Active Object Properties", 'OVERLAY', 4),
        ('4', "Cursor", "3D Cursor Properties", 'ORIENTATION_CURSOR', 5)
            ]
    return items

def metapanel_camera_sections():
    items = [
        ('0', "Settings", "Camera Settings", 'PRESET', 1),
        ('1', "Actions", "Camera Quick Actions", 'PLAY', 2),
        ('2', "Transforms", "Camera Transform", 'ORIENTATION_VIEW', 4),
        ('3', "Display", "Camera Viewport Display Settings", 'OVERLAY', 8),
        ('4', "Cursor", "3D Cursor Properties", 'ORIENTATION_CURSOR', 16)
            ]
    return items


class WLT_SceneProperties(PropertyGroup):
    debug: BoolProperty(
                            name="Debug",
                            description="WLT Debug Mode",
                            default=True,
                            options={'SKIP_SAVE'}
                             )

    mode_flag: IntProperty(
        name="Mode Flag",
        description="A flag for modes",
        options={'ANIMATABLE'}

    )


class WLT_ObjectProperties(PropertyGroup):
    debug: BoolVectorProperty(
                            name="Debug Switches",
                            description="WLT Gizmo Toolbox",
                            default=(False, False, False, False),
                            size=4,
                            options={'SKIP_SAVE'}
                             )


# WIRE COLORS
class WLTWireColors(PropertyGroup):

    default_obj_wire: FloatVectorProperty(
                                        name="Object Wireframe Color",
                                        description="Default Object Mode Wire Color",
                                        default=(0.0, 0.0, 0.0),
                                        subtype='COLOR_GAMMA',
                                        min=0.0,
                                        max=1.0,
                                        )

    default_edit_wire: FloatVectorProperty(
                                        name="Edit Mode Wireframe Color",
                                        description="Default Edit Mode Wire Color",
                                        default=(0.0, 0.0, 0.0),
                                        subtype='COLOR_GAMMA',
                                        min=0.0,
                                        max=1.0,
                                        )

    temp_obj_wire: FloatVectorProperty(
                                        name="Object Wireframe Color",
                                        description="Temporary Object Mode Wire Color",
                                        default=(0.0, 0.0, 0.0),
                                        subtype='COLOR_GAMMA',
                                        min=0.0,
                                        max=1.0,
                                        )

    temp_edit_wire: FloatVectorProperty(
                                        name="Edit Mode Wireframe Color",
                                        description="Temporary Edit Mode Wire Color",
                                        default=(0.0, 0.0, 0.0),
                                        subtype='COLOR_GAMMA',
                                        min=0.0,
                                        max=1.0,
                                        )


def fast_snap_prev_modes(get):
    if get == 'PIVOT':
        items = [
            ('BOUNDING_BOX_CENTER', "Bounding Box Center", "", 'NONE', 1),
            ('CURSOR', "3D Cursor", "", 'NONE', 2),
            ('INDIVIDUAL_ORIGINS', "Individual Origins", "", 'NONE', 3),
            ('MEDIAN_POINT', "Median Point", "", 'NONE', 4),
            ('ACTIVE_ELEMENT', "Active Element", "", 'NONE', 5),
                ]
    elif get == 'TARGET':
        items = [
            ('CLOSEST', "Closest", "", 'NONE', 1),
            ('CENTER', "Center", "", 'NONE', 2),
            ('MEDIAN', "Median", "", 'NONE', 3),
            ('ACTIVE', "Active", "", 'NONE', 4),
                ]
    else:
        items = [
            ('CLOSEST', "Closest", "", 'NONE', 1),
            ('CENTER', "Center", "", 'NONE', 2),
            ('MEDIAN', "Median", "", 'NONE', 3),
            ('ACTIVE', "Active", "", 'NONE', 4),
                ]
    return items


class FastSnapProps(PropertyGroup):
    pivot_items = fast_snap_prev_modes(get='PIVOT')
    prev_pivot: EnumProperty(
        name='',
        description='Prior Pivot Mode',
        items=pivot_items
    )

    target_items = fast_snap_prev_modes(get='TARGET')
    prev_pivot: EnumProperty(
        name='',
        description='Prior Snap Target',
        items=target_items
    )

    snap_state: IntProperty(
                                name="Snap State",
                                min=0,
                                max=5,
                                default=0
                             )


class CustomPopoverProps(PropertyGroup):

    popover_1: StringProperty(
        name="Custom Popover 1",
        description="Stores the name of a panel",
        default="BATMAN",
    )

    popover_2: StringProperty(
        name="Custom Popover 2",
        description="Stores the name of a panel",
        default="BATMAN",
    )

    popover_3: StringProperty(
        name="Custom Popover 3",
        description="Stores the name of a panel",
        default="BATMAN",
    )


def generate_list_enum(self, context):
    prefs = bpy.context.preferences
    WLT_prefs = prefs.addons[__package__].preferences
    items = WLT_prefs.keymap_group_filter.split(', ')

    to_filter = []

    for item in items:
        to_filter.append(  (item, item, item,)   )

    return to_filter

class WLT_BrushProperties(PropertyGroup):
    """
    Per-brush properties that hold references
    to things like disabled masks, etc.
    """
    tex: PointerProperty(
        type=bpy.types.Texture,
        name="Stored reference to ",
        description="MAGIC",
    )

    mask_tex: PointerProperty(
        type=bpy.types.Texture,
        name="Stored reference to ",
        description="MAGIC",
    )



class WLT_PaintProperties(PropertyGroup):
    """
    Texture Paint Stuff. Per-workspace
    """

    tex: PointerProperty(
        type=bpy.types.Texture,
        name="Stored reference to ",
        description="MAGIC",
    )



class WLT_WorkspaceProperties(PropertyGroup):
    """
    Root group for WLT properties that can be
    configured per-workspace. Mostly panel tabs.
    """
    # Top-level debug flag
    debug: BoolProperty(
                            name="Debug",
                            description="WLT Debug Mode",
                            default=True,
                            options={'SKIP_SAVE'}
                             )


    ### Meta Panel Stuff ###
    mp_tabs: EnumProperty(
        name='',
        description='Current Tab',
        items=metapanel_layout_items()
    )

    mp_active_subsections: BoolVectorProperty(
                            name="Active Object Panel Sub-Section Toggles",
                            description="WLT Gizmo Toolbox",
                            default=(False, False, False, False),
                            size=4,
                            options={'SKIP_SAVE'}
                             )

    mp_cam_index: IntProperty(
        name="Camera Index",
        default=0
    )

    camera_stuff = metapanel_camera_sections()

    mp_cam_sections: EnumProperty(
        name='',
        description="subsections for the camera tab",
        items=camera_stuff,
        options={'ENUM_FLAG'},
        default=None
    )

    mp_shading_cavtoggle: BoolVectorProperty(
                                    name="Cavity Shading",
                                    description="WLT Cavity Toggles",
                                    default=(False, False),
                                    size=2,
                                    options={'SKIP_SAVE'}
                                     )

    mp_transforms: PointerProperty(type=CustomTransforms)

    mp_debug: BoolVectorProperty(
                            name="MetaPanelDebugFlags",
                            description="WLT Gizmo Toolbox",
                            default=(False, False, False, False),
                            size=4,
                            options={'SKIP_SAVE'}
                             )

    ### Quick-Menu ###
    qm_items = [
        ('EDIT', "Edit Menu", "Edit Mesh", 'NONE', 1),
        ('ADD', "Add Menu", "Add Mesh", 'NONE', 2),
        ('UV', 'UV Map Menu', "UV Map Options", 'NONE', 3),
        ('CONTEXT', "Context Menu", "Right-Click Menu", 'NONE', 4),
        ('VERTEX', "Vertex Menu", "Vertex Operators", 'NONE', 5),
        ('EDGE', "Edge Menu", "Edge Operators", 'NONE', 6),
        ('FACE', "Face Menu", "FAce Operators", 'NONE', 7)
            ]

    qm_menus: EnumProperty(
        name='',
        description='Current Menu',
        items=qm_items
    )

    ### Custom Popovers ###
    popovers: PointerProperty(type=CustomPopoverProps)


    ### Fast Panel
    fp_tab_items = [
                ('MEASURES', "Measures", "Measurement Tools and Overlays", 'DESKTOP', 1),
                ('OVERLAYS', "Overlays", "Viewport Overlays", 'SEQ_STRIP_DUPLICATE', 2),
                ('NORMALS', "Normals", "Mesh Normal Overlays", 'SNAP_FACE_CENTER', 3),
                ('GIZMOS', "Gizmos", "Gizmo Options", 'CON_OBJECTSOLVER', 4),
                ('DISPLAY', "Display", "Object Display Options", 'RIGID_BODY_CONSTRAINT', 5)
                           ]

    fp_tabs: EnumProperty(
        name=' ',
        description='Fast Panel Tabs',
        items=fp_tab_items
    )

    ### View Pie ###
    vp_orbit_target: PointerProperty(
        type=bpy.types.Object,
        name="Reference Object",
        description="MAGIC",
    )

    vp_use_global_target: BoolProperty(
        name="Use Global Orbit Target",
        default=False
    )

    ### Keymap Filters ###
    group_filter_enum: EnumProperty(
        name='',
        description='Current Tab',
        items=generate_list_enum
    )

    ### Wire Color Manager ###
    wire_colors: PointerProperty(type=WLTWireColors)

    ### Modal State Tracking ###
    modal_state: PointerProperty(type=ModalProps)

    ### Snap State Tracking ###
    snap_state: PointerProperty(type=FastSnapProps)

    ### Gizmo Stuff ###
    gizmos: PointerProperty(type=WLT_GizmoProperties)


class WLT_WindowProperties(PropertyGroup):
    """
    Root group for WLT properties that can be
    configured per-workspace. Mostly panel tabs.
    """
    # Top-level debug flag
    debug: BoolProperty(
            name="Debug",
            description="WLT Debug Mode",
            default=True,
            options={'SKIP_SAVE'}
            )

    last_tap: FloatProperty(
        name="Last Tap",
        description="Previous key-down time",
        default=-1.00000,
        precision=6,
    )

    quick_threshold: FloatProperty(
        name="Quick Tap Time",
        description="Time threshold for quick taps",
        default=0.50
    )

    hard_threshold: FloatProperty(
        name="Hard Tap Time",
        description="Force threshold for hard taps",
        default=0.2
    )


    tap_seq: IntVectorProperty(
        name="Tap Sequence",
        description="The current sequence of taps",
        size=9,
        default=(-1, -1, -1, -1, -1, -1, -1, -1, -1),
    )

    combo_seq: StringProperty(
        name="Tap Combo",
        default=""
    )

OUT = [
    FastPanelProps,
    ObjectMatrixConversions,
    CustomTransforms,
    WLTWireColors,
    FastSnapProps,
    CustomPopoverProps,
    ModalProps,
    WLT_GizmoProperties,
    WLT_ObjectProperties,
    WLT_SceneProperties,
    WLT_WorkspaceProperties,
    WLT_WindowProperties,
    WLT_BrushProperties,
]

def register():
    for cls in OUT:
        bpy.utils.register_class(cls)

    bpy.types.Object.WLT = PointerProperty(type=WLT_ObjectProperties)
    bpy.types.Scene.WLT = PointerProperty(type=WLT_SceneProperties)
    bpy.types.WindowManager.WLT = PointerProperty(type=WLT_WindowProperties)
    bpy.types.WorkSpace.WLT = PointerProperty(type=WLT_WorkspaceProperties)
    bpy.types.Brush.WLT = PointerProperty(type=WLT_BrushProperties)

def unregister():
    del bpy.types.WorkSpace.WLT
    del bpy.types.WindowManager.WLT
    del bpy.types.Scene.WLT
    del bpy.types.Object.WLT
    del bpy.types.Brush.WLT

    for cls in OUT:
        bpy.utils.unregister_class(cls)