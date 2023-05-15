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

import os
import json
import bpy
from bpy.app.handlers import persistent
from pathlib import Path


class WLT_WORKSPACE_MANAGER(object):
    """This object handles external config files"""

    active_config = {}
    active_config_path = ""

    @persistent
    def load_workspace_config(self):
        possible_configs = []
        if bpy.data.filepath:
            directory = os.path.dirname(bpy.data.filepath)
            for subdir, dirs, files in os.walk(directory):
                for filename in files:
                    filepath = subdir + os.sep + filename
                    if (filename.startswith("bl_")) and filepath.endswith(".JSON"):
                        possible_configs.append(filepath)

        if len(possible_configs) == 0:
            self.clear_config()

        if len(possible_configs) == 1:
            self.load_config(possible_configs[0])

        if len(possible_configs) > 1:
            print("Multiple Configurations Found!")


    def load_config(self, path, force_refresh=False):
        """Called from the post_load handler"""

        if not os.path.isfile(path):
            print("Config Not Found!")
            return False

        if path == self.active_config_path:
            print("Config already Loaded")
            if not force_refresh:
                return False

        with open(path) as json_file:
            self.active_config = json.load(json_file)
            self.apply_config()


    def apply_config(self):
        """Iterates through the active config to find and apply applicable settings"""
        print("Applying Workspace Config...")
        for name, value in self.active_config.items():
            if name.startswith("workspace."):
                if type(value) == dict:
                    print("recursive!")


    def clear_config(self):
        self.active_config = {}
        self.active_config_path = ""


    def register(self):
        bpy.app.handlers.load_post.append(self.load_workspace_config)


    def unregister(self):
        bpy.app.handlers.load_post.remove(self.load_workspace_config)


