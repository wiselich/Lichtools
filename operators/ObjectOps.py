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
    FloatProperty, StringProperty,
    EnumProperty,
    IntProperty,
    BoolProperty,
    FloatVectorProperty,
)
import random

class WLT_OT_AddBasePlane(bpy.types.Operator):
    bl_idname = "wlt.add_base_plane"
    bl_label = "WLT Add Base Plane"
    bl_description = ("Cycles between cameras in a scene "
                      "by changing the view layer's active camera.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.mesh.primitive_plane_add(
            size=1, calc_uvs=False, enter_editmode=False)
        # bpy.ops.transform.resize(value=[xdim, ydim, 1.0])
        # bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # bpy.context.active_object.hide_viewport = True
        bpy.context.active_object.hide_render = True
        bpy.context.active_object.display_type = "WIRE"
        bpy.context.active_object.display.show_shadows = False

        # bpy.context.active_object.name = objname

        new_obj = bpy.context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        return {"FINISHED"}

class WLT_OT_RandomizeObjectPass(bpy.types.Operator):
    bl_idname = "wlt.randomize_pass"
    bl_label = "WLT Randomize Object Pass"
    bl_description = ("Randomizes the object pass for "
                      "selected editable objects.")
    bl_options = {'REGISTER'}

    min: IntProperty(
        name="Minimum Index",
        description="",
        default=0
    )

    max: IntProperty(
        name="Maximum Index",
        description="",
        default=32
    )

    def execute(self, context):
        for obj in context.selected_editable_objects:
            obj.pass_index = random.randint(self.min, self.max)

        return {"FINISHED"}

class WLT_OT_RandomizeObjectColor(bpy.types.Operator):
    bl_idname = "wlt.randomize_obj_color"
    bl_label = "WLT Randomize Object Color"
    bl_description = ("Randomizes the object color for "
                      "selected editable objects.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        for obj in context.selected_editable_objects:
            obj.color = (random.random(), random.random(), random.random(), 1.0)

        return {"FINISHED"}

class WLT_OT_Add_Light(bpy.types.Operator):
    bl_idname = "wlt.add_light"
    bl_label = "WLT Add Light"
    bl_description = ("It adds "
                      "the light")
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    bl_property = "light_type"

    light_type_items = [
        ("POINT", "Point Light", "Emits light equally in all directions", 1),
        ("SUN", "Sun", "Emits light from an infinitely distant point", 2),
        ("SPOT", "Spot Light", "Emits light in a cone", 3),
        ("AREA", "Area Light", "Emits light from a flat surface, like a soft box", 4),
    ]

    light_type: EnumProperty(
        items=light_type_items,
        name="Light Type",
        description="Which transform slot to set/get/update",
        default='SPOT',
    )

    rgb: FloatVectorProperty(
        name="Color",
        description="Light Color",
        default=(1.0, 1.0, 1.0),
        size=3,
        min=0.0,
        max=1.0,
        subtype='COLOR'
    )

    spec_factor: FloatProperty(
        name="Specular",
        default=1.0,
        min=0.0,
        max=9999.0,
        soft_max=1.0,
        subtype='FACTOR'
    )

    energy: FloatProperty(
        name="Power",
        default=10.0,
        subtype='POWER'
    )

    soft_shadow: FloatProperty(
        name="Radius",
        default=0.25,
        subtype='DISTANCE'
    )

    use_shadow: BoolProperty(
        name="Cast Shadows",
        default=True
    )

    contact_shadows: BoolProperty(
        name="Contact Shadows",
        default=True
    )

    cshadow_bias: FloatProperty(
        name="Contact Shadow Bias",
        default=0.03,
        min=0.001
    )

    cshadow_distance: FloatProperty(
        name="Contact Shadow Distance",
        default=0.2,
        min=0.0,
        subtype='DISTANCE'
    )

    cshadow_thickness: FloatProperty(
        name="Contact Shadow Thickness",
        default=0.2,
        min=0.0,
        subtype='DISTANCE'
    )

    spot_size: FloatProperty(
        name="Spotlight Size",
        default=0.785398,
        min=0.0,
        subtype='ANGLE'
    )

    spot_blend: FloatProperty(
        name="Spotlight Blend",
        default=0.2,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )

    spot_show_cone: BoolProperty(
        name="Spotlight Show Cone",
        default=False
    )

    sun_angle: FloatProperty(
        name="Sun Angle",
        default=0.00918043,
        min=0.0,
        subtype='ANGLE'
    )

    area_shape_items = [
        ("SQUARE", "Square", "", 1),
        ("RECTANGLE", "Rectangle", "", 2),
        ("DISK", "Disk", "", 3),
        ("ELLIPSE", "Ellipse", "", 4),
    ]

    area_shape: EnumProperty(
        items=area_shape_items,
        name="Area Light Shape",
        description="The shape of the area light",
        default='SQUARE',
    )

    area_size_x: FloatProperty(
        name="Area Light Size",
        default=0.25,
        min=0.0,
        subtype='DISTANCE'
    )

    area_size_y: FloatProperty(
        name="Area Light Size",
        default=0.25,
        min=0.0,
        subtype='DISTANCE'
    )

    cycles_max_bounces: IntProperty(
        name="Max Light Bounces",
        default=1024,
        min=1,
    )

    cycles_multi_importance: BoolProperty(
        name="Cycles Multi Importance Sampling",
        default=True
    )

    cycles_area_portal: BoolProperty(
        name="Cycles Area Portal",
        default=False
    )


    def execute(self, context):
        view_layer = context.view_layer

        light_data = bpy.data.lights.new(name="WLT Light Data", type=self.light_type)

        light_data.energy = self.energy
        light_data.color = self.rgb

        light_data.specular_factor = self.spec_factor
        
        light_data.use_shadow = self.use_shadow

        light_data.shadow_soft_size = self.soft_shadow

        light_data.use_contact_shadow = self.contact_shadows
        light_data.contact_shadow_bias = self.cshadow_bias
        light_data.contact_shadow_distance = self.cshadow_distance
        light_data.contact_shadow_thickness = self.cshadow_thickness

        if self.light_type == 'POINT':
            pass
        elif self.light_type == 'SUN':
            light_data.angle = self.sun_angle
        elif self.light_type == 'SPOT':
            light_data.spot_size = self.spot_size
            light_data.spot_blend = self.spot_blend
            light_data.show_cone = self.spot_show_cone
        else:
            light_data.size = self.area_size_x
            light_data.size_y = self.area_size_y

        if context.engine == 'CYCLES':
            light_data.cycles.max_bounces = self.cycles_max_bounces
            light_data.cycles.use_multiple_importance_sampling = self.cycles_multi_importance
            if self.light_type == 'AREA':
                light_data.cycles.is_portal = self.cycles_area_portal

        light_object = bpy.data.objects.new(name="WLT Light", object_data=light_data)
        light_object.location = context.scene.cursor.location
        view_layer.active_layer_collection.collection.objects.link(light_object)

        return {"FINISHED"}


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


    def draw(self, context):
        layout = self.layout
        root = layout.column(align=True)
        root.use_property_split = True
        root.use_property_decorate = False

        type_row = root.row(align=True)
        type_row.prop(
            self,
            "light_type",
        )

        if self.light_type == 'POINT':
            pass
        elif self.light_type == 'SUN':
            root.prop(
                self,
                "sun_angle"
            )
        elif self.light_type == 'SPOT':
            root.prop(
                self,
                "spot_size"
            )
            root.prop(
                self,
                "spot_blend"
            )
            root.prop(
                self,
                "spot_show_cone"
            )
        else:
            root.prop(
                self,
                "area_shape",
                text=""
            )
            root.prop(
                self,
                "area_size_x",
                text="Size X"
            )
            root.prop(
                self,
                "area_size_y",
                text="Size Y"
            )

        root.label(text="Common Settings")

        root.prop(
           self,
           "rgb",
           text="Color"
        )
        root.prop(
           self,
           "energy"
        )
        root.prop(
           self,
           "spec_factor"
        )
        root.prop(
           self,
           "soft_shadow"
        )

        row = root.row(align=True)
        row.use_property_split = False
        row.prop(
            self,
            "contact_shadows"
        )
        if self.contact_shadows:
            root.prop(
                self,
                "cshadow_bias",
                text="Bias"
            )
            root.prop(
                self,
                "cshadow_distance",
                text="Distance"
            )
            root.prop(
                self,
                "cshadow_thickness",
                text="Thickness"
            )

OUT = [
    WLT_OT_AddBasePlane,
    WLT_OT_RandomizeObjectPass,
    WLT_OT_RandomizeObjectColor,
    WLT_OT_Add_Light,
]