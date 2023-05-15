import bpy

from .VPCursorGizmo import ATVPCursorGizmo
from .VPCursorGizmo import ATCursorTool
from .TabletGizmo import WLT_TabletGizmoGroup
from .MirrorGizmo import WLT_MirrorGizmoGroup
from .ScreenGizmo import WLT_FlatGizmo
from .PivotGizmo import WLT_PivotGizmoGroup

def register():
    bpy.utils.register_class(ATVPCursorGizmo)
    bpy.utils.register_class(WLT_TabletGizmoGroup)
    bpy.utils.register_class(WLT_MirrorGizmoGroup)
    bpy.utils.register_class(WLT_FlatGizmo)
    bpy.utils.register_class(WLT_PivotGizmoGroup)

    bpy.utils.register_tool(ATCursorTool)

def unregister():
    bpy.utils.unregister_class(ATVPCursorGizmo)
    bpy.utils.unregister_class(WLT_TabletGizmoGroup)
    bpy.utils.unregister_class(WLT_MirrorGizmoGroup)
    bpy.utils.unregister_class(WLT_FlatGizmo)
    bpy.utils.unregister_class(WLT_PivotGizmoGroup)

    bpy.utils.unregister_tool(ATCursorTool)
