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

#  __  __     __   ___      __
# |__)|_  /\ |  \   | |__||(_ 
# | \ |__/--\|__/   | |  ||__)
# 
# This module is likely a bad idea. Seriously.
# Globals are messy. And this is a module of global-ish things.
# Tread cautiously.

from . import (
    gizmo_manager,
    keymap_manager,
    rhythm_manager,
    env_manager,
    workspace_system
)

GM = gizmo_manager.WLT_GIZMO_MANAGER()
KM = keymap_manager.WLT_KEYMAP_GLOBALS()
RM = rhythm_manager.WLT_RHTHYM_MANAGER()
EN = env_manager.WLT_ENVIRONMENT_MANAGER()
WM = workspace_system.WLT_WORKSPACE_MANAGER()

def register():
    print("Begin Keymap Register")
    KM.register_default_maps()
    ...

def unregister():
    KM.unregister_all()
    ...