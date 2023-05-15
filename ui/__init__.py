from . import (
    AnimPanel,
    ContextPies,
    EditMenu,
    FastPanel,
    MetaPanel,
    ViewPanel,
    ViewPie,
    ViewportAppends
)

import bpy

OUT = (
    AnimPanel.OUT
    + ContextPies.OUT
    + EditMenu.OUT
    + FastPanel.OUT
    + MetaPanel.OUT
    + ViewPanel.OUT
    + ViewPie.OUT
)

def register():
    for cls in OUT:
        bpy.utils.register_class(cls)

    for cls in ViewportAppends.OUT:
        bpy.types.VIEW3D_HT_header.append(cls)

def unregister():
    for cls in OUT:
        bpy.utils.unregister_class(cls)

    for cls in ViewportAppends.OUT:
        bpy.types.VIEW3D_HT_header.remove(cls)

    