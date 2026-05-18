import bpy
from bpy.props import BoolProperty
from bpy.types import AddonPreferences

addon_keymaps = []


def _update_shortcuts(self, context):
    register_keymaps(self if self.use_shortcuts else None)


class RIGPANEL_AddonPreferences(AddonPreferences):
    bl_idname = "Rigging_Panel"

    use_shortcuts: BoolProperty(
        name="Enable Default Shortcuts",
        description="Register default hotkeys (changeable in Keymap preferences)",
        default=True,
        update=_update_shortcuts,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_shortcuts")
        layout.label(text="Default shortcuts (Pose mode):")
        col = layout.column(align=True)
        col.label(text="Shift+Ctrl+M — Mute constraints on selected bones")
        col.label(text="Shift+Ctrl+U — Unmute constraints on selected bones")
        col.label(text="Shift+Ctrl+R — Reveal / unhide all bones")
        layout.label(text="Edit in Edit → Preferences → Keymap → Rigging Panel")


def register_keymaps(prefs):
    unregister_keymaps()

    if not prefs or not prefs.use_shortcuts:
        return

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return

    km = kc.keymaps.new(name="Pose", space_type="EMPTY")

    kmi = km.keymap_items.new("rigpanel.set_constraints_state", type="M", value="PRESS", shift=True, ctrl=True)
    kmi.properties.mute = True
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("rigpanel.set_constraints_state", type="U", value="PRESS", shift=True, ctrl=True)
    kmi.properties.mute = False
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("rigpanel.reveal_bones", type="R", value="PRESS", shift=True, ctrl=True)
    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    bpy.utils.register_class(RIGPANEL_AddonPreferences)


def unregister():
    unregister_keymaps()
    bpy.utils.unregister_class(RIGPANEL_AddonPreferences)
