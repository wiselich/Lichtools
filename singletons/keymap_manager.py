import bpy
import os
import json
import datetime
import threading

import pathlib

from .utils import (path_to_dict, package)

class WLT_KEYMAP_GLOBALS(object):
    """
    A global object that contains and manages keymap data
    
    NOTE: Doesn't play nicely with the first hot-reload
    """

    # These are the raw file paths to JSON dictionaries
    default_paths = {}
    user_paths = {}

    # These are the straight-from-JSON dictionaries
    default_maps = {}
    usermaps = {}

    # This is the dictonary of actually-registered-in-blender keymap items
    blender_maps = {} 

    # default_content = pathlib.Path(os.path.realpath(__file__)).parent

    def __init__(self):
        print("Loading Keymap Manager")
        default_paths = self.default_paths
        default_maps = self.default_maps

        default_paths['ASHER'] = pathlib.Path(os.path.realpath(__file__)).parents[1] / 'cfg' / 'asherskeys.JSON'

        for name, dict_path in self.default_paths.items():
            default_maps.update({name: self.path_to_dict(dict_path)})


    def path_to_dict(self, dict_path):
        """Path goes in, dict comes out. Can't explain that."""
        if not os.path.isfile(dict_path):
            print("Config Not Found!")
        with open(dict_path) as json_file:
            keydict = json.load(json_file)
        return keydict


    def get_default_maps(self):
        return self.default_maps


    def register_default_maps(self):
        """
        Call in module register func
        """
        default_maps = self.default_maps

        for name, keymap in default_maps.items():
            self.register_bl_map(name, keymap)


    def add_user_map(self, name, path, overwrite=False):
        usermaps = self.usermaps
        if (name in usermaps) and not overwrite:
            print("USER KEYMAP already exists! Aborting.")
            return False

        usermaps.update({name:path})
        return True


    def get_user_map(self, name):
        usermap = self.usermap

        if name in usermap:
            return usermap[name]
        else:
            print("Keymap not Found")
            return False

    def load_user_JSON_directory(directory):
        from pathlib import Path
        dir_path = Path(directory)

        if not dir_path.is_dir():
            print("Warning: Invalid Directory")

        configs = []

        for subdir, dirs, files, in os.walk(dir_path):
            for filename in files:
                filepath = subdir + os.sep + filename
                if filepath.endswith(".JSON"):
                    configs.append(filepath)

        with open(directory) as json_file:
            keydict = json.load(json_file)
        return keydict


    def delete_user_map(self, name):
        usermaps = self.usermaps

        if name in usermaps:
            del usermaps[name]
            return True
        else:
            print("Keymap not Found")
            return False


    def add_bl_map(self, name, bl_map, overwrite=False):
        """This method doesn't register the keymap. Use register_bl_map for that"""
        blender_maps = self.blender_maps

        if (name in blender_maps) and not overwrite:
            print("Keymap already exists! Aborting.")
            return False

        blender_maps.update({name:bl_map})
        return True


    def get_bl_map(self, name):
        blender_maps = self.blender_maps

        if name in blender_maps:
            return blender_maps[name]
        else:
            print("Keymap not found")
            return False


    def register_bl_map(self, name, input_map):
        wm = bpy.context.window_manager
        prefs = bpy.context.preferences
        WLT_prefs = prefs.addons[package].preferences
        kc = wm.keyconfigs.addon
        refmap = wm.keyconfigs.active

        keymaps = []
        i = 1

        for group, operators in input_map.items():
            print("registering", group)
            if group in WLT_prefs.keymap_group_filter.split(', '):
                # Rudimentary group-based filtering
                # Groups don't mean anything to Blender itself
                # They're just an organizational structure I've adapted
                print("filtering group", group)
                continue

            for op, props in operators.items():
                keymap = props.get("keymap")
                space_type = props.get("space_type", "EMPTY")
                if keymap:
                    ref = refmap.keymaps.find(name=str(keymap), space_type=space_type)

                    if ref:
                        km = kc.keymaps.new(name=str(keymap), space_type=space_type)

                        idname = props.get("idname")
                        key_type = props.get("type")
                        value = props.get("value")

                        shift = props.get("shift", False)
                        ctrl = props.get("ctrl", False)
                        alt = props.get("alt", False)
                        any_mod = props.get("any", False)
                        key_mod = props.get("key_mod", "NONE")

                        kmi = km.keymap_items.new(idname, key_type, value, shift=shift, ctrl=ctrl, alt=alt, any=any_mod, key_modifier=key_mod)
                        if kmi:
                            if properties := props.get("properties"):
                                for name, value in properties.items():
                                    setattr(kmi.properties, name, value)

                            keymaps.append((km, kmi))
                        else:
                            print("KMI Didn't")
                    else:
                        print("Keymap Not Found: " + keymap)
                else:
                    print("KM Not Found for " + str(props.get("idname")))

        self.add_bl_map(name, keymaps)


    def unregister_bl_map(self, name, remove=False):
        blender_maps = self.blender_maps

        if not name in blender_maps:
            print("Keymap not found!")
            return False

        for km, kmi in blender_maps[name]:
            km.keymap_items.remove(kmi)

        if remove:
            del blender_maps[name]

        return True


    def unregister_all(self):
        """
        Call in module unregister func
        """
        blender_maps = self.blender_maps

        for bl_map in blender_maps.keys():
            self.unregister_bl_map(bl_map)

        self.blender_maps = {}
        self.default_maps = {}
        self.usermaps = {}
        self.default_paths = {}
        self.user_paths = {}


    def draw_keydict(self, keydict, layout):
        import rna_keymap_ui
        wm = bpy.context.window_manager
        prefs = bpy.context.preferences
        WLT_prefs = prefs.addons[package].preferences
        kc = wm.keyconfigs.addon


        for group, operators in keydict.items():
            if group in WLT_prefs.keymap_group_filter.split(', '):
                # Rudimentary group-based filtering
                # Groups don't mean anything to Blender itself
                # They're just an organizational structure I've adapted
                print("filtering")
                continue

            for op, props in operators.items():
                keymap = props.get("keymap")
                space_type = props.get("space_type", "EMPTY")

                if keymap:
                    ref = kc.keymaps.get(keymap)

                    kmi = None
                    if ref:
                        idname = props.get("idname")

                        for entry in ref.keymap_items:
                            if entry.idname == idname:
                                op_props = props.get("properties")

                                if op_props:
                                    if all([
                                        getattr(entry.properties, name, None) 
                                        == name for name in op_props
                                        ]):
                                        
                                        break
                                
                                kmi = entry

                    if kmi:
                        
                        box = layout.column()
                        col = box.column()
                        rna_keymap_ui.draw_kmi(["ADDON", "USER", "DEFAULT"], kc, ref, kmi, col, 0)