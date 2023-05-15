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
import mathutils
from bpy.props import (
    BoolProperty, StringProperty,
    PointerProperty,
    EnumProperty,
    # IntProperty
)


class WLT_OT_Zoop(bpy.types.Operator):
    """Lets the user cycle between cameras in the scene.
        Mostly meant to be called from the UI, given how it handles
        input properties."""
    bl_idname = "wlt.zoop"
    bl_label = "WLT Set Camera"
    bl_description = ("Cycles between cameras in a scene "
                      "by changing the view layer's active camera.")
    bl_options = {'REGISTER'}

    target_camera: StringProperty(
                        name="Target Camera",
                        description="The camera to cycle to.",
                        maxlen=1024,
    )

    def invoke(self, context, event):
        target = self.target_camera

        speed_default = context.preferences.view.smooth_view

        context.preferences.view.smooth_view = 500

        if (target == context.space_data.camera.name):
            bpy.ops.view3d.view_camera(
                        'INVOKE_DEFAULT',
                        False,
            )
        else:
            if context.region_data.view_perspective == 'CAMERA':
                context.region_data.view_perspective = 'PERSP'

            bpy.ops.wm.context_set_id(
                    'INVOKE_DEFAULT',
                    False,
                    data_path="space_data.camera",
                    value=target
            )

            bpy.ops.view3d.view_camera(
                        'INVOKE_DEFAULT',
                        False,
            )

        context.preferences.view.smooth_view = speed_default

        return {'FINISHED'}


class WLT_OT_Lock_Camera(bpy.types.Operator):
    """Locks the location and rotation of the selected camera"""
    bl_idname = "wlt.lock_camera"
    bl_label = "WLT Lock Camera"
    bl_description = ("Toggles rotation and location locks "
                      "for the selected camera.")
    bl_options = {'BLOCKING', 'UNDO', 'REGISTER'}

    target_object: StringProperty(
                        name="Target Object",
                        description="The object to select.",
    )

    def invoke(self, context, event):

        obj = bpy.data.objects.get(self.target_object)

        if False in obj.lock_location or False in obj.lock_rotation:
            obj.lock_location = [True, True, True]
            obj.lock_rotation = [True, True, True]
        else:
            obj.lock_location = [False, False, False]
            obj.lock_rotation = [False, False, False]

        return {'FINISHED'}


class WLT_OT_Add_Camera_Keying_Set(bpy.types.Operator):
    """Makes a keying set for camera transforms"""
    bl_idname = "wlt.add_camera_keyset"
    bl_label = "WLT Add Camera Keyset"
    bl_description = ("Adds and activates a keying set "
                      "for camera settings.")
    bl_options = {'BLOCKING', 'UNDO', 'REGISTER'}

    auto_add: BoolProperty(
        name="Auto-Add",
        description=("Automatically add the selected camera's "
                     "transform channels to the keying set"),
        default=True
    )

    def invoke(self, context, event):
        target_object = context.active_object

        for keying_set in context.scene.keying_sets:
            if keying_set.bl_label == "CameraKeys":
                self.report({'WARNING'}, "Keying Set Already Exists; Aborting")
                return{'CANCELLED'}

        bpy.ops.anim.keying_set_add(
                'INVOKE_DEFAULT',
                False,
                )
        keyset = context.scene.keying_sets.active
        keyset.bl_label = "CameraKeys"

        if self.auto_add:
            if not len(keyset.paths) == 0:
                self.report({'WARNING'}, "You have done the impossible; Aborting")
                return{'CANCELLED'}

            if not target_object:
                self.report({'WARNING'}, "No Target; Aborting")
                return{'CANCELLED'}
        
            keyset.paths.add(
                target_id=target_object,
                data_path="location",
                index=-1,
            )
            keyset.paths.add(
                target_id=target_object,
                data_path="rotation_euler",
                index=-1,
            )

            if target_object.type == 'CAMERA':
                cam = target_object.data

                keyset.paths.add(
                    target_id=cam,
                    data_path="lens",
                    index=-1,
                )

                if cam.dof.use_dof:
                    keyset.paths.add(
                        target_id=cam,
                        data_path="dof.focus_distance",
                        index=-1,
                    )

                    keyset.paths.add(
                        target_id=cam,
                        data_path="dof.aperture_fstop",
                        index=-1,
                    )

        return {'FINISHED'}


class WLT_OT_Create_Camera(bpy.types.Operator):
    """Handles routine stuff like duplicating transforms and settings"""
    bl_idname = "wlt.create_camera"
    bl_label = "WLT Create Camera"
    bl_description = ("Toggles rotation and location locks "
                      "for the selected camera.")
    bl_options = {'BLOCKING', 'UNDO', 'REGISTER'}

    settings_mode_items = [
        ("LINKED", "Linked Settings", "Creates a camera with a linked datablock", 1),
        ("DUPLICATED", "Duplicated Settings", "Creates a camera with the same settings as the active camera", 2),
        ("BLENDER_DEFAULT", "Default Settings", "Creates a bog-standard camera", 3),
        ("ASHER_DEFAULT", "Asher's Settings", "Weird Stuff", 4),
    ]

    settings_mode: EnumProperty(
        items=settings_mode_items,
        name="Camera Settings",
        description="Which transform slot to set/get/update",
        default='ASHER_DEFAULT',
    )

    transform_mode_items = [
        ("AT_CURSOR", "Create at Cursor", "Creates the camera at the 3D Cursor pocation", 1),
        ("AT_VIEWPORT", "Create at Viewport", "Creates the camera at the Viewport position", 2),
        ("AT_ACTIVE", "Create at Active", "Creates the camera at the active camera's location", 3),
        ("AT_ORIGIN", "Create at Origin", "Creates the camera at the world origin", 4),
    ]

    transform_mode: EnumProperty(
        items=transform_mode_items,
        name="Camera Settings",
        description="Which transform slot to set/get/update",
        default='AT_VIEWPORT',
    )

    view_cam: BoolProperty(
        name="View After Creation",
        default=True
    )

    def invoke(self, context, event):
        wm = context.window_manager
        view_layer = context.view_layer

        region = context.region
        rv3d = context.region_data
        view_loc = rv3d.view_location

        if self.settings_mode == 'LINKED':
            if context.scene.camera:
                cam = context.scene.camera.data
            else:
                cam = bpy.data.cameras.new(name="WLT Camera Data")
        elif self.settings_mode == 'DUPLICATED':
            if context.scene.camera:
                cam = context.scene.camera.data.copy()
            else:
                cam = bpy.data.cameras.new(name="WLT Camera Data")
        elif self.settings_mode == 'BLENDER_DEFAULT':
            cam = bpy.data.cameras.new(name="WLT Camera Data")
            cam.display_size = 2
        else:
            cam = bpy.data.cameras.new(name="WLT Camera Data")
            cam.sensor_width = 50
            cam.lens = 35
            cam.display_size = 2
            cam.show_name = True

        cam_object = bpy.data.objects.new(name="WLT Camera", object_data=cam)
        view_layer.active_layer_collection.collection.objects.link(cam_object)

        if self.transform_mode == 'AT_CURSOR':
            cam_object.location = context.scene.cursor.location
            cam_object.rotation_euler = context.scene.cursor.rotation_euler
        elif self.transform_mode == 'AT_VIEWPORT':
            view_quat = mathutils.Quaternion(context.region_data.view_rotation)
            cam_object.location = rv3d.view_matrix.inverted().to_translation()
            cam_object.rotation_euler = view_quat.to_euler()
            pass
        elif self.transform_mode == 'AT_ACTIVE':
            if context.scene.camera:
                cam_object.location = context.scene.camera.location
                cam_object.rotation_euler = context.scene.camera.rotation_euler
            pass
        else:
            pass

        if self.view_cam:
            bpy.ops.wlt.zoop(
                        'INVOKE_DEFAULT',
                        False,
                        target_camera=cam_object.name
            )

        return {'FINISHED'}

OUT = [
    WLT_OT_Zoop,
    WLT_OT_Lock_Camera,
    WLT_OT_Add_Camera_Keying_Set,
    WLT_OT_Create_Camera
]