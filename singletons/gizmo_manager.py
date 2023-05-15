import bpy

class WLT_GIZMO_MANAGER(object):
    """
    It's like the regional gizmo_map, but in python.
    """

    # For gizmos we don't expect to ensure and unlink over and over.
    # These gizmos should have low-impact poll functions
    persistent_gizmos = {}

    # For transient gizmos.
    # They might be modal-only, or their scope is narrow enough that
    # it's better to launch them from an operator, rather than polling.
    temporary_gizmos = {}

    # A string:bool dictionary 
    state_map = {}

    # A string:gizmo dictionary
    gizmo_list = {}

    def add_persistent(self, name, gizmo):
        p_gizmos = self.persistent_gizmos

        if name in p_gizmos:
            print("gizmo already exists!")
            return False

        p_gizmos.update({name: gizmo})
        return True


    def toggle_temp(self, name):
        t_gizmos = self.temporary_gizmos

        if name in t_gizmos:
            bpy.context.window_manager.gizmo_group_type_unlink_delayed(name)
            del t_gizmos[name]
        else:
            t_gizmos.update({name: str(name)})
            bpy.context.window_manager.gizmo_group_type_ensure(name)


    # Called in setup() functions so we can access the gizmo objects themselves later on.
    def register_gizmo(self, name, region, gizmo):
        gz_list = self.gizmo_list
        gz_id = region + "." + name

        gz_list.update({gz_id: gizmo})
        return True