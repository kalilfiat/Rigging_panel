import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from ..utils import context as rig_context


class RIGPANEL_OT_toggle_armature_display(Operator):
    bl_idname = "rigpanel.toggle_armature_display"
    bl_label = "Toggle Armature Display"
    bl_options = {"REGISTER", "UNDO"}

    target: EnumProperty(
        name="Target",
        items=(
            ("IN_FRONT", "In Front", ""),
            ("AXES", "Axes", ""),
            ("NAMES", "Names", ""),
        ),
    )

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}

        if self.target == "IN_FRONT":
            armature.show_in_front = not armature.show_in_front
        elif self.target == "AXES":
            armature.data.show_axes = not armature.data.show_axes
        elif self.target == "NAMES":
            armature.data.show_names = not armature.data.show_names

        return {"FINISHED"}


class RIGPANEL_OT_set_display_type(Operator):
    bl_idname = "rigpanel.set_display_type"
    bl_label = "Set Display Type"
    bl_options = {"REGISTER", "UNDO"}

    display_type: EnumProperty(
        name="Display Type",
        items=(
            ("OCTAHEDRAL", "Octahedral", ""),
            ("STICK", "Stick", ""),
            ("BBONE", "B-Bone", ""),
            ("ENVELOPE", "Envelope", ""),
            ("WIRE", "Wire", ""),
        ),
    )

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        armature.data.display_type = self.display_type
        return {"FINISHED"}


class RIGPANEL_OT_reveal_bones(Operator):
    bl_idname = "rigpanel.reveal_bones"
    bl_label = "Reveal Bones"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}

        for bone in armature.data.bones:
            bone.hide = False

        for collection in armature.data.collections_all:
            if hasattr(collection, "is_visible"):
                collection.is_visible = True

        self.report({"INFO"}, "All bones revealed.")
        return {"FINISHED"}


class RIGPANEL_OT_toggle_weight_overlay(Operator):
    bl_idname = "rigpanel.toggle_weight_overlay"
    bl_label = "Toggle Weight Overlay"
    bl_description = "Toggle viewport overlay that displays vertex weights (View3D overlays)"
    bl_options = {"REGISTER"}

    def execute(self, context):
        overlays = []
        for win in getattr(context.window_manager, "windows", []) or []:
            for area in win.screen.areas:
                if area.type != "VIEW_3D":
                    continue
                space = area.spaces.active
                if getattr(space, "type", None) != "VIEW_3D":
                    continue
                ov = space.overlay
                if hasattr(ov, "show_weight"):
                    overlays.append(ov)

        if not overlays:
            self.report({"WARNING"}, "No 3D Viewport overlays available.")
            return {"CANCELLED"}

        reference = overlays[0].show_weight
        new_state = not reference
        for ov in overlays:
            ov.show_weight = new_state

        state = "on" if new_state else "off"
        self.report({"INFO"}, f"Weight overlay {state}.")
        return {"FINISHED"}


classes = (
    RIGPANEL_OT_toggle_armature_display,
    RIGPANEL_OT_set_display_type,
    RIGPANEL_OT_reveal_bones,
    RIGPANEL_OT_toggle_weight_overlay,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
