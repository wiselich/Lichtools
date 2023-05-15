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

class WLT_OT_create_temp_scene(bpy.types.Operator):
    bl_idname = "wlt.temp_scene"
    bl_label = "WLT Isolate in Temporary Scene"
    bl_description = "Links the selected collection into a temporary scene, disabling it in the active view layer of the source scene"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):

        collection = bpy.context.collection
        bpy.context.view_layer.active_layer_collection.exclude = True
        
        old_scene = bpy.context.scene
        old_scene_name = old_scene.name

        bpy.ops.scene.new(type='EMPTY') # This automatically changes the scene
        bpy.context.scene.background_set = bpy.data.scenes[old_scene_name]

        new_scene = bpy.context.scene
        new_scene_name = new_scene.name = "temp_scene"

        print(new_scene.collection.objects.__dir__())

        new_scene.collection.children.link(collection)

        return {'FINISHED'}


OUT = [
    WLT_OT_create_temp_scene
]
