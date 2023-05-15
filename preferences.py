# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import os
import rna_keymap_ui
import json

from functools import (
    cache
)

# Keymap stuff stolen from MESHmachine
# Get Machine's addons, they're awesome!

def get_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_name():
    return os.path.basename(get_path())

# This function is memoized so it can be called in the UI without
# slamming the thread with OS calls
@cache
def get_prefs():
    return bpy.context.preferences.addons[get_name()].preferences


# This is a generic recursive reader I yoinked from Kite
def recursive_dict_print(target_dict):
    for key, value in target_dict.items():
        if type(value) is dict:
            print("Entering:   ", key)
            recursive_dict_print(value)
        else:
            print(key, ":", value)

# Remove?
def get_keymap_item(name, idname, key, alt=False, ctrl=False, shift=False):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    km = kc.keymaps.get(name)
    kmi = km.keymap_items.get(idname)

    if kmi:
        if all([kmi.type == key and kmi.alt is alt and kmi.ctrl is ctrl and kmi.shift is shift]):
            return True
    return False


class WLTAddonPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    path = get_path()
    bl_idname = __package__

    keymap_group_filter: bpy.props.StringProperty(
            name="Keymap Group Filter",
            description="A comma separated list of keymap groups to filter",
            default="",
            )

    keymap_operator_filter: bpy.props.StringProperty(
            name="Keymap Operator Filter",
            description="A comma-separates list of operators to filter out of the keymap",
            default="",
            )

    user_keymap_path: bpy.props.StringProperty(
            name="Keymap Path",
            description="Where you can plug in your personal keymap dict",
            default="",
            subtype='FILE_PATH'
            )

    prefs_tab_items = [
                        ("GENERAL", "General", ""),
                        ("KEYS", "Keymap", ""),
                      ]

    prefs_baseKeymap_items = [
                              ("ASHER", "Asher's Config",
                               "Restart Blender or click the "
                               "refresh button on the right to enable"),
                              ("HUMANS", "Basic Config",
                               "Restart Blender or click the "
                               "refresh button on the right to enable"),
                              # ("ABOUT", "About", "")
                             ]

    tabs: bpy.props.EnumProperty(
                                name="Tabs",
                                items=prefs_tab_items,
                                default="GENERAL",
                                )

    baseKeymap: bpy.props.EnumProperty(
                                name="Tabs",
                                items=prefs_baseKeymap_items,
                                default="ASHER",
                                )

    category: bpy.props.StringProperty(
            name="Tab Category",
            description="Choose a name for the category of the panel",
            default="WLT",
            # update=update_panel
            )
    
    tablet_modal: bpy.props.BoolProperty(
        name="In Tablet Modal",
        default = False
    )

    def draw_keymaps(self, layout, kmap=0, debug=False):
        wm = bpy.context.window_manager

        # Hacky selector to change what key config we're showing
        if kmap == 0:
            kc = wm.keyconfigs.addon
        elif kmap == 1:
            kc = wm.keyconfigs.active
        else:
            kc = wm.keyconfigs.user

        from . singletons import KM

        column = layout.column(align=True)
        column.separator()

        header = column.row(align=False)
        header.label(text="Base Keymap")
        header.prop(self, "baseKeymap", expand=True)
        header.operator(
            "script.reload",
            text="",
            icon='FILE_REFRESH'
        )

        header = column.row(align=False)
        header.label(text="Supplementary Keymap")
        header.prop(self, "user_keymap_path", text="")

        column.separator()

        if self.baseKeymap == 'ASHER':
            for name, keylist in KM.default_maps.items():
                KM.draw_keydict(keylist, column)

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, "tabs", expand=True)

        box = column.column(align=True)

        if self.tabs == "GENERAL":
            self.draw_general_tab(box)
        elif self.tabs == "KEYS":
            self.draw_keymap_tab(box)
        # elif self.tabs == "ABOUT":
        #     self.draw_about_tab(box)

    def draw_general_tab(self, box):
        col = box.column(align=True)

        col.separator(factor=2)
        row = col.row(align=True)
        row.prop(self, "keymap_group_filter")

        labelrow = col.row(align=True)
        labelrow.alignment = 'CENTER'
        labelrow.prop(self, "category", text="")
        labelrow.label(text=" Sidebar Tab:"
                            ""
                            ""
                            "")

        subcol = col.column(align=True)
        subrow = subcol.split(factor=0.2)
        subrow.label(text="Overlays:")
        subrow.label(text="A massive panel "
                          "with (almost) every overlay "
                          "setting")

        subrow = subcol.split(factor=0.2)
        subrow.label(text="Meta Panel:")
        subrow.label(text="A tabbed panel/popover with "
                          "Overlays, Object Properties, etc, "
                          "for fullscreen modeling"
                          "")

        col.separator(factor=2)

        labelrow = col.row(align=True)
        labelrow.alignment = 'CENTER'
        labelrow.label(text="Pies:"
                            ""
                            ""
                            "")

        subcol = col.column(align=True)

        subrow = subcol.split(factor=0.2)
        subrow.label(text="WLT View Pie:")
        subrow.label(text="Viewport snapping, "
                          "Rotation Modes, "
                          "and related settings")

        subrow = subcol.split(factor=0.2)
        subrow.label(text="WLT Selection Pie:")
        subrow.label(text="Select Inner/Outer, "
                          "Flat Faces, Loops, NGons, etc"
                          "")

        subrow = subcol.split(factor=0.2)
        subrow.label(text="WLT Transform Pie:")
        subrow.label(text="Toggle or cycle common "
                          "transformation settings "
                          "(snapping mode, pivot, etc)")

        subrow = subcol.split(factor=0.2)
        subrow.label(text="WLT Orientation Pie:")
        subrow.label(text="Switch between various "
                          "transform orientations "
                          "")

        subrow = subcol.split(factor=0.2)
        subrow.label(text="WLT Cursor Pie:")
        subrow.label(text="Does 3D Cursor Things"
                          ""
                          "")

        col.separator(factor=2)

        labelrow = col.row(align=True)
        labelrow.alignment = 'CENTER'
        labelrow.label(text="Menus:"
                            ""
                            ""
                            "")

        subcol = col.column(align=True)

        subrow = subcol.split(factor=0.2)
        subrow.label(text="WLT Modeling Menu:")
        subrow.label(text="A shortlist of common "
                          "operators, with shortcuts for "
                          "quick access")

        col.separator(factor=2)

        labelrow = col.row(align=True)
        labelrow.alignment = 'CENTER'
        labelrow.label(text="Operators:"
                            ""
                            ""
                            "")

        subcol = col.column(align=True)

        subrow = subcol.split(factor=0.2)
        subrow.label(text="WLT Set Axis:")
        subrow.label(text="Snaps the viewport to an "
                          "isometric angle"
                          "")

    def draw_keymap_tab(self, box, debug=False):

        split = box.split()
        b = split.box()
        self.draw_keymaps(b, 2, True)
