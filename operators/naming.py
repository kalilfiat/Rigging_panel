import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator

from ..utils import context as rig_context


KNOWN_SIDE_SUFFIXES = (
    ".L", ".R", "_L", "_R", "-L", "-R",
    ".l", ".r", "_l", "_r", "-l", "-r",
)

KNOWN_PREFIXES = (
    "CTRL_", "DEF_", "MCH_", "IK_", "FK_", "ORG_", "TGT_", "VIS_", "WGT_",
)


def strip_side_suffix(name):
    for suf in sorted(KNOWN_SIDE_SUFFIXES, key=len, reverse=True):
        if name.endswith(suf):
            return name[: -len(suf)]
    return name


def strip_known_prefix(name):
    for pre in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if name.startswith(pre):
            return name[len(pre):]
    return name


def _rename_bones(context, armature, bones, name_builder):
    if context.mode == "EDIT_ARMATURE":
        pairs = [(edit_bone, name_builder(strip_side_suffix(edit_bone.name))) for edit_bone in bones]
        for index, (edit_bone, _name) in enumerate(pairs):
            edit_bone.name = f"__rigtmp_{index}"
        for edit_bone, new_name in pairs:
            edit_bone.name = new_name
    else:
        pairs = [(pose_bone.bone, name_builder(strip_side_suffix(pose_bone.bone.name))) for pose_bone in bones]
        for index, (bone, _name) in enumerate(pairs):
            bone.name = f"__rigtmp_{index}"
        for bone, new_name in pairs:
            bone.name = new_name
    return len(pairs)


class RIGPANEL_OT_apply_name_prefix(Operator):
    bl_idname = "rigpanel.apply_name_prefix"
    bl_label = "Apply Name Prefix"
    bl_options = {"REGISTER", "UNDO"}

    prefix: StringProperty(name="Prefix", default="")
    strip_existing: BoolProperty(name="Strip Known Prefixes", default=True)

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        if not rig_context.require_pose_or_edit_mode(self, context):
            return {"CANCELLED"}

        if context.mode == "EDIT_ARMATURE":
            bones = rig_context.selected_edit_bones(context)
        else:
            bones = rig_context.selected_pose_bones(context)

        if not bones:
            self.report({"WARNING"}, "Select one or more bones first.")
            return {"CANCELLED"}

        prefix = self.prefix

        def build(base):
            core = strip_known_prefix(base) if self.strip_existing else base
            if prefix and core.startswith(prefix):
                return core
            return f"{prefix}{core}" if prefix else core

        count = _rename_bones(context, armature, bones, build)
        self.report({"INFO"}, f"Renamed {count} bone(s).")
        return {"FINISHED"}


class RIGPANEL_OT_apply_name_suffix(Operator):
    bl_idname = "rigpanel.apply_name_suffix"
    bl_label = "Apply Name Suffix"
    bl_options = {"REGISTER", "UNDO"}

    suffix: StringProperty(name="Suffix", default=".L")

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        if not rig_context.require_pose_or_edit_mode(self, context):
            return {"CANCELLED"}

        if context.mode == "EDIT_ARMATURE":
            bones = rig_context.selected_edit_bones(context)
        else:
            bones = rig_context.selected_pose_bones(context)

        if not bones:
            self.report({"WARNING"}, "Select one or more bones first.")
            return {"CANCELLED"}

        suffix = self.suffix

        def build(base):
            return f"{base}{suffix}"

        count = _rename_bones(context, armature, bones, build)
        self.report({"INFO"}, f"Renamed {count} bone(s).")
        return {"FINISHED"}


class RIGPANEL_OT_apply_full_bone_name(Operator):
    bl_idname = "rigpanel.apply_full_bone_name"
    bl_label = "Apply Prefix + Suffix"
    bl_options = {"REGISTER", "UNDO"}

    prefix: StringProperty(name="Prefix", default="")
    suffix: StringProperty(name="Suffix", default="")

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        if not rig_context.require_pose_or_edit_mode(self, context):
            return {"CANCELLED"}

        if context.mode == "EDIT_ARMATURE":
            bones = rig_context.selected_edit_bones(context)
        else:
            bones = rig_context.selected_pose_bones(context)

        if not bones:
            self.report({"WARNING"}, "Select one or more bones first.")
            return {"CANCELLED"}

        prefix = self.prefix
        suffix = self.suffix

        def build(base):
            core = strip_known_prefix(base)
            if prefix:
                core = f"{prefix}{core}"
            if suffix:
                core = f"{core}{suffix}"
            return core

        count = _rename_bones(context, armature, bones, build)
        self.report({"INFO"}, f"Renamed {count} bone(s).")
        return {"FINISHED"}


classes = (
    RIGPANEL_OT_apply_name_prefix,
    RIGPANEL_OT_apply_name_suffix,
    RIGPANEL_OT_apply_full_bone_name,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
