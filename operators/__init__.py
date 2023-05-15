from . import (
    asset_ops,
    CameraOps,
    MeshOps,
    ModifierOps,
    NodeOps,
    ObjectOps,
    PaintOps,
    scene_ops,
    SculptOps,
    SelectOps,
    TabletOps,
    ThemeOps,
    TransformOperators,
    UtilityOps,
    ViewportOps,
    wrappers
)

import bpy

OUT = (
    asset_ops.OUT
    + CameraOps.OUT
    + MeshOps.OUT
    + ModifierOps.OUT
    + NodeOps.OUT
    + ObjectOps.OUT
    + PaintOps.OUT
    + scene_ops.OUT
    + SculptOps.OUT
    + SelectOps.OUT
    + TabletOps.OUT
    + ThemeOps.OUT
    + TransformOperators.OUT
    + UtilityOps.OUT
    + ViewportOps.OUT
    + wrappers.OUT
)

def register():
    for cls in OUT:
        bpy.utils.register_class(cls)

def unregister():
    for cls in OUT:
        bpy.utils.unregister_class(cls)