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
import mathutils
import bmesh

from bpy.props import (
    FloatProperty,
    EnumProperty,
    BoolProperty,
)


class WLT_OT_SuperContextMenu(bpy.types.Operator):
    """Edit Mode Context menu for out-of-mode objects"""
    bl_idname = "wlt.moar_context"
    bl_label = "WLT Moar Context"
    bl_description = "I heard you like context menus, so I put some context in your context menu"

    def invoke(self, context, event):
        m_x = event.mouse_region_x
        m_y = event.mouse_region_y
        m_loc = (m_x, m_y)

        self.m_loc = m_loc

        bpy.ops.view3d.select(
            'INVOKE_REGION_WIN',
            False,
            extend=False,
            center=True,
            object=True,
            location=self.m_loc
        )

        override = bpy.context.copy()

        for obj in context.selected_objects:
            for ed_obj in context.objects_in_mode:
                if not obj.data == ed_obj.data:
                    override['edit_object'] = None

        def draw_menu(self, context):
            menu = self.layout
            menu.operator_context = 'INVOKE_DEFAULT'

            op = menu.operator("wlt.add_to_mode", text="Add to Mode")
            op.mouse_loc = m_loc

            op = menu.operator("wlt.move_cursor", text="Cursor to Origin")
            op.move_mode = 'RED'

            op = menu.operator("wlt.move_cursor", text="Vanilla Cursor to Origin")
            op.move_mode = 'GREEN'

        wm = context.window_manager
        wm.popup_menu(draw_func=draw_menu, title="", icon='NONE')
        return {'FINISHED'}


class WLT_OT_SelectThrough(bpy.types.Operator):
    """Wrapper for editmode_toggle that uses overrides to enable mode expansion"""
    bl_idname = "wlt.select_through"
    bl_label = "WLT Select Through"
    bl_description = "Give your balls a tug, Shorsey"

    def modal(self, context, event):
        def flerb(context):
            override = bpy.context.copy()
            override['window'] = context.window
            bpy.ops.mesh.select_mode(
                override,
                'INVOKE_DEFAULT',
                False,
                type='FACE',
                use_expand=True
            )

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            bpy.app.timers.register(bpy.ops.mesh.select_mode, first_interval=1)
            return {'FINISHED', 'PASS_THROUGH'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        m_x = event.mouse_region_x
        m_y = event.mouse_region_y
        m_loc = (m_x, m_y)

        self.m_loc = m_loc

        bpy.ops.mesh.select_mode(
            'INVOKE_REGION_WIN',
            False,
            type='VERT',
        )
        op = bpy.ops.view3d.select_box(
            'INVOKE_REGION_WIN',
            False,
            wait_for_input=False
        )
        print(str(op))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

#############################################
##  Proximity Select & Related utilities   ##
#############################################


def average_list(lst):
    """
    Returns the average of a list of values.\n
    Meant for averaging vector lists.
    """ 

    if isinstance(lst, list):
        v_sum = mathutils.Vector((0.0, 0.0, 0.0))

        for v in lst:
            v_sum += v

        return v_sum / float(len(lst))
    else:
        print("NOT A LIST")



def find_shortest_distance(obj_a, obj_b):
    """
    Given two mesh objects and an iteration limit, 
    this function finds and refines a shortest-distance line 
    between the objects' evaluated geometry.
    """

    if not ((obj_a.type == 'MESH') and (obj_b.type =='MESH')):
        print("These Aren't Mesh Objects")
        return False, obj_a.location, obj_b.location

    # Location of obj_b in obj_a's local space
    b_loc = obj_a.matrix_world.inverted() @ obj_b.location

    # Get closest point on obj_a, in obj_a's local space
    success_a, point_a, normal_a, index_a = obj_a.closest_point_on_mesh(b_loc)
    #Convert point_a to world space
    point_a = obj_a.matrix_world @ point_a
    point_a_out = point_a
    #convert point_a to obj_b's local space
    point_a = obj_b.matrix_world.inverted() @ point_a


    # Get closest point on obj_b, in obj_b's local space
    success_b, point_b, normal_b, index_b = obj_b.closest_point_on_mesh(point_a)
    #Convert point_b to world space
    point_b = obj_b.matrix_world @ point_b
    point_b_out = point_b
    #convert point_b to obj_a's local space
    point_b = obj_a.matrix_world.inverted() @ point_b

    success = (success_a and success_b)

    return success, point_a_out, point_b_out


def build_obj_tree(context, objects, use_geometry_center=False):
    """
    Builds a KD Tree for the supplied list of objects. \n
    The (bool) use_geometry_center toggles whether the location 
    is taken from the object origin or the averaged geometry location.
    """

    size = len(objects)
    tree = mathutils.kdtree.KDTree(size)

    for i, obj in enumerate(objects):
        if use_geometry_center:
            if obj.type == 'MESH':
                bm = bmesh.new(context.evaluated_depsgraph_get())
                bm.from_object(obj)

                coords = []

                for v in bm.verts:
                    coords.append(v.co)

                loc = average_list(coords)
            else:
                loc = obj.location

            tree.insert(loc, i)
        else:
            tree.insert(obj.location, i)

    tree.balance()

    return tree


def calc_distance(vec_a, vec_b, dist):
    """
    Returns the Euclidian distance between two points in 3D Space.\n

    How is there not a built-in function for this?
    """
    return (vec_b - vec_a).magnitude


def refine_tree(obj, tree, radius, dist, refine=True):
    """
    Takes in a KD Tree of objects and performs a two-step distance filter. \n

    First it gets the objects with origins within (float) radius distance of (object) obj, 
    then it (optionally) refines that list to those with geometry that is within (float) dist distance of obj's geometry. 
    """

    # Lazy bounding box center, so objects with offset origins don't produce weird results
    vec_sum = mathutils.Vector((0.0, 0.0, 0.0))
    for vec in obj.bound_box:
        vec_sum += mathutils.Vector(vec)

    bbox_center = obj.location + (vec_sum/8.0)

    # The tree only contains vectors and indicies.
    # This gives us a list of objects within the search radius.
    objs = []
    for (co, index, rad) in tree.find_range(bbox_center, radius):
        ob = bpy.context.selectable_objects[index]
        if (ob.type == 'MESH') and not (ob == obj):
            objs.append(bpy.context.selectable_objects[index])

    if not refine:
        print("SKIP")
        return objs

    filtered_objs = []

    for ob in objs:
        if ob == obj:
            pass

        flag, point_a, point_b = find_shortest_distance(obj, ob)

        if not flag:
            print("ERROR")

        raw_dist = calc_distance(point_a, point_b, dist)

        if raw_dist <= dist:
            filtered_objs.append(ob)

    return filtered_objs


class WLT_OT_ProximitySelect(bpy.types.Operator):
    """A select operator that uses a KD Tree to find objects near the 3D Cursor"""
    bl_idname = "wlt.prox_select"
    bl_label = "WLT Proximity Select"
    bl_description = "Magic"

    mode_items = [
        ("ACTIVE", "Near Active", "Selects items based on their proximity to the active object", 1),
        ("CURSOR", "Near Cursor", "Selects items based on their proximity to the 3D cursor", 2),
    ]

    mode: EnumProperty(
        items=mode_items,
        name="Mode",
        description="Which transform slot to set/get/update",
        default='ACTIVE',
    )

    refine: BoolProperty(
        name="Refine Search",
        description="Whether to use the Refinement Distance "
                    "to refine the selection based on the distance "
                    "from the object's geometry.",
        default=True,
    )

    radius: FloatProperty(
        name="Sample Radius",
        description="The search radius to find objects in",
        default=10,
        unit = 'LENGTH',
        subtype = 'DISTANCE',
    )

    dist: FloatProperty(
        name="Refinement Distance",
        description="The refinement distance",
        default=1,
        unit = 'LENGTH',
        subtype = 'DISTANCE',
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        size = len(bpy.context.selectable_objects)
        tree = mathutils.kdtree.KDTree(size)

        for i, obj in enumerate(bpy.context.selectable_objects):
            tree.insert(obj.location, i)

        tree.balance()

        if self.mode == 'CURSOR':
            loc = context.scene.cursor.location

            for (co, index, dist) in tree.find_range(loc, self.radius):
                bpy.context.selectable_objects[index].select_set(True)

            return {'FINISHED'}
        else:
            raw_bounds = context.active_object.bound_box         

            bounds = []
            for point in raw_bounds:
                bounds.append(mathutils.Vector(point).magnitude)

            # TODO: Remove magic number
            scaled_radius = max(bounds)/1.25 + self.radius
            scaled_distance = self.dist

            objs = refine_tree(context.active_object, tree, scaled_radius, scaled_distance, self.refine)
            for ob in objs:
                ob.select_set(True)
            return {'FINISHED'}

OUT = [
    WLT_OT_SuperContextMenu,
    WLT_OT_SelectThrough,
    WLT_OT_ProximitySelect,
]