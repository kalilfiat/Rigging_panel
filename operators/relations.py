import bpy
from bpy.types import Operator

from ..utils import context as rig_context


class RIGPANEL_OT_clear_bone_parent(Operator):
    bl_idname = "rigpanel.clear_bone_parent"
    bl_label = "Clear Parent"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}

        names = rig_context.require_selected_bones(self, context)
        if not names:
            return {"CANCELLED"}

        previous_mode = context.mode
        rig_context.activate_armature(context, armature)

        bpy.ops.object.mode_set(mode="EDIT")

        name_set = set(names)
        for edit_bone in armature.data.edit_bones:
            selected = edit_bone.name in name_set
            edit_bone.select = selected
            edit_bone.select_head = selected
            edit_bone.select_tail = selected

        bpy.ops.armature.parent_clear(type="CLEAR")

        if previous_mode == "POSE":
            bpy.ops.object.mode_set(mode="POSE")
        elif previous_mode == "EDIT_ARMATURE":
            bpy.ops.object.mode_set(mode="EDIT")
        else:
            bpy.ops.object.mode_set(mode="OBJECT")

        self.report({"INFO"}, f"Cleared parent on {len(names)} bone(s).")
        return {"FINISHED"}


class RIGPANEL_OT_flip_head_tail(Operator):
    bl_idname = "rigpanel.flip_head_tail"
    bl_label = "Head Tail Flip"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}

        names = rig_context.require_selected_bones(self, context)
        if not names:
            return {"CANCELLED"}

        previous_mode = context.mode
        rig_context.activate_armature(context, armature)

        if previous_mode != "EDIT_ARMATURE":
            bpy.ops.object.mode_set(mode="EDIT")

        flipped = 0
        for name in names:
            edit_bone = armature.data.edit_bones.get(name)
            if edit_bone is None:
                continue
            old_head = edit_bone.head.copy()
            edit_bone.head = edit_bone.tail
            edit_bone.tail = old_head
            flipped += 1

        if previous_mode == "POSE":
            bpy.ops.object.mode_set(mode="POSE")
        elif previous_mode == "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        elif previous_mode == "EDIT_ARMATURE":
            bpy.ops.object.mode_set(mode="EDIT")

        self.report({"INFO"}, f"Flipped {flipped} bone(s).")
        return {"FINISHED"}


classes = (
    RIGPANEL_OT_clear_bone_parent,
    RIGPANEL_OT_flip_head_tail,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
