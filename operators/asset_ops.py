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

import bpy

class WLT_OT_Wrap_Selected_In_Collection(bpy.types.Operator):
    bl_idname = "wlt.wrap_with_collection"
    bl_label = "WLT Wrap Selected With Collection"
    bl_description = (
        "Wraps the selected objects in a collection named after the first object"
    )
    bl_options = {'REGISTER', 'UNDO'}

    reset_transform: bpy.props.BoolProperty (
        name="Reset Transform",
        description="Reset the object's location, rotation, and scale",
        default=True
    )
    mark_asset: bpy.props.BoolProperty (
        name="Mark Asset",
        description="Mark the resultant collection as an Asset",
        default=True
    )
    asset_tags: bpy.props.StringProperty (
        name="Tags to Apply",
        description="A comma-separated list of asset tags to apply",
        default=""
    )

    def wrap(self, obj: bpy.types.Object, context):
        view_layer = bpy.context.view_layer
        active_collection = view_layer.active_layer_collection.collection
        new_collection = bpy.data.collections.new(name = obj.name)

        active_collection.children.link(new_collection)

        for col in obj.users_collection:
            col.objects.unlink(obj)

        new_collection.objects.link(obj)

        if self.reset_transform:
            obj.location = (0.0, 0.0, 0.0)

        if self.mark_asset:
            new_collection.asset_mark()
            if len(self.asset_tags) > 0:
                for tag in self.asset_tags.split(","):
                    tag = tag.strip()
                    new_collection.asset_data.tags.new(name=tag, skip_if_exists=True)

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            self.wrap(obj, context)

        return {'FINISHED'}

OUT = [
    WLT_OT_Wrap_Selected_In_Collection
]