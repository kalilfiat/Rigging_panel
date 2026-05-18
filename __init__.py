# bl_info must be first and literal so Blender recognises the addon when installing from ZIP.

bl_info = {
    "name": "Rigging Utility Panel",
    "author": "TechArt Tools",
    "version": (0, 2, 3),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Rig Tools",
    "description": "Compact rigging utility shelf for batch bone operations and rig debugging.",
    "category": "Rigging",
}

import bpy

from . import preferences, ui
from .operators import constraints, deform, display, naming, pose, relations, shapes_colors, validation
from .utils import context as context_utils

modules = (
    context_utils,
    preferences,
    display,
    shapes_colors,
    constraints,
    deform,
    naming,
    relations,
    pose,
    validation,
    ui,
)


def register():
    for module in modules:
        module.register()
    addon_entry = bpy.context.preferences.addons.get("Rigging_Panel")
    if addon_entry:
        preferences.register_keymaps(addon_entry.preferences)


def unregister():
    preferences.unregister_keymaps()
    for module in reversed(modules):
        module.unregister()
