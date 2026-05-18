from bpy.props import EnumProperty, FloatVectorProperty
from bpy.types import Operator

import bpy

from ..utils import context as rig_context


def _assign_custom_rgb(color_slot, rgb):
    """Apply RGB to BoneColor.custom (Bone.color / PoseBone.color wrappers stay readonly)."""
    rgb = tuple(max(0.0, min(1.0, float(c))) for c in rgb)
    sel = tuple(min(c + 0.18, 1.0) for c in rgb)
    act = tuple(min(c + 0.32, 1.0) for c in rgb)

    color_slot.palette = "CUSTOM"
    custom = color_slot.custom

    for attr_name, value in (("normal", rgb), ("select", sel), ("active", act)):
        if hasattr(custom, attr_name):
            target = getattr(custom, attr_name)
            try:
                target[:] = value
                continue
            except Exception:
                pass
            try:
                setattr(custom, attr_name, value)
            except Exception:
                pass

    if hasattr(custom, "solid"):
        try:
            solid = getattr(custom, "solid")
            solid[:] = (*rgb, 1.0)
        except Exception:
            try:
                custom.solid = (*rgb, 1.0)
            except Exception:
                pass


class RIGPANEL_OT_pick_custom_shape(Operator):
    bl_idname = "rigpanel.pick_custom_shape"
    bl_label = "Pick Active Object as Shape"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = rig_context.get_settings(context)
        obj = context.object
        if not obj or obj.type == "ARMATURE":
            self.report({"WARNING"}, "Select a non-armature object to use as a custom shape.")
            return {"CANCELLED"}
        settings.custom_shape_object = obj.name
        return {"FINISHED"}


class RIGPANEL_OT_apply_custom_shape(Operator):
    bl_idname = "rigpanel.apply_custom_shape"
    bl_label = "Apply Custom Shape"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        if not rig_context.require_pose_or_edit_mode(self, context):
            return {"CANCELLED"}
        names = rig_context.require_selected_bones(self, context)
        if not names:
            return {"CANCELLED"}

        settings = rig_context.get_settings(context)
        shape = bpy.data.objects.get(settings.custom_shape_object)
        if shape is None:
            self.report({"WARNING"}, "Pick or type a valid shape object first.")
            return {"CANCELLED"}

        if context.mode != "POSE":
            bpy.ops.object.mode_set(mode="POSE")

        for pose_bone in rig_context.pose_bones_from_names(armature, names):
            pose_bone.custom_shape = shape

        self.report({"INFO"}, f"Applied shape to {len(names)} bone(s).")
        return {"FINISHED"}


class RIGPANEL_OT_clear_custom_shape(Operator):
    bl_idname = "rigpanel.clear_custom_shape"
    bl_label = "Clear Custom Shape"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        if not rig_context.require_pose_or_edit_mode(self, context):
            return {"CANCELLED"}
        names = rig_context.require_selected_bones(self, context)
        if not names:
            return {"CANCELLED"}

        if context.mode != "POSE":
            bpy.ops.object.mode_set(mode="POSE")

        for pose_bone in rig_context.pose_bones_from_names(armature, names):
            pose_bone.custom_shape = None

        self.report({"INFO"}, f"Cleared shapes on {len(names)} bone(s).")
        return {"FINISHED"}


def _restore_mode(previous_mode):
    if previous_mode == "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    elif previous_mode == "EDIT_ARMATURE":
        bpy.ops.object.mode_set(mode="EDIT")
    elif previous_mode == "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def _apply_edit_bone_colors(armature, names, color):
    count = 0
    for name in names:
        edit_bone = armature.data.edit_bones.get(name)
        if edit_bone is None:
            continue
        _assign_custom_rgb(edit_bone.color, color)
        count += 1
    return count


def _apply_pose_bone_colors(armature, names, color):
    count = 0
    for pose_bone in rig_context.pose_bones_from_names(armature, names):
        _assign_custom_rgb(pose_bone.color, color)
        count += 1
    return count


class RIGPANEL_OT_apply_bone_color(Operator):
    bl_idname = "rigpanel.apply_bone_color"
    bl_label = "Apply Bone Color"
    bl_options = {"REGISTER", "UNDO"}

    color: FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=3,
        min=0.0,
        max=1.0,
        default=(0.25, 0.55, 1.0),
    )
    apply_to: EnumProperty(
        name="Apply To",
        items=(
            ("EDIT", "Edit Bone", "Rest/edit bone color (Edit Armature mode)"),
            ("POSE", "Pose Bone", "Pose bone color (Pose mode)"),
            ("BOTH", "Both", "Edit bone color in Edit mode, then pose color in Pose mode"),
        ),
        default="EDIT",
    )

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        if not rig_context.require_pose_or_edit_mode(self, context):
            return {"CANCELLED"}
        names = rig_context.require_selected_bones(self, context)
        if not names:
            return {"CANCELLED"}

        previous_mode = context.mode
        applied = 0

        if self.apply_to in {"EDIT", "BOTH"}:
            if context.mode != "EDIT_ARMATURE":
                bpy.ops.object.mode_set(mode="EDIT")
            applied += _apply_edit_bone_colors(armature, names, self.color)

        if self.apply_to in {"POSE", "BOTH"}:
            if context.mode != "POSE":
                bpy.ops.object.mode_set(mode="POSE")
            applied += _apply_pose_bone_colors(armature, names, self.color)

        if previous_mode != context.mode:
            _restore_mode(previous_mode)

        self.report({"INFO"}, f"Applied color ({self.apply_to.lower()}) on {len(names)} bone(s).")
        return {"FINISHED"}


classes = (
    RIGPANEL_OT_pick_custom_shape,
    RIGPANEL_OT_apply_custom_shape,
    RIGPANEL_OT_clear_custom_shape,
    RIGPANEL_OT_apply_bone_color,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
