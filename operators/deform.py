import bpy
from bpy.props import BoolProperty
from bpy.types import Operator

from ..utils import bone_selection
from ..utils import context as rig_context


class RIGPANEL_OT_set_deform(Operator):
    bl_idname = "rigpanel.set_deform"
    bl_label = "Set Bone Deform"
    bl_options = {"REGISTER", "UNDO"}

    use_deform: BoolProperty(name="Use Deform", default=True)

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        if not rig_context.require_pose_or_edit_mode(self, context):
            return {"CANCELLED"}
        names = rig_context.require_selected_bones(self, context)
        if not names:
            return {"CANCELLED"}

        if context.mode == "EDIT_ARMATURE":
            for name in names:
                edit_bone = armature.data.edit_bones.get(name)
                if edit_bone is not None:
                    edit_bone.use_deform = self.use_deform
        else:
            for bone in rig_context.data_bones_from_names(armature, names):
                bone.use_deform = self.use_deform

        self.report({"INFO"}, f"Updated deform on {len(names)} bone(s).")
        return {"FINISHED"}


class RIGPANEL_OT_select_by_deform(Operator):
    bl_idname = "rigpanel.select_by_deform"
    bl_label = "Select Bones by Deform"
    bl_options = {"REGISTER", "UNDO"}

    use_deform: BoolProperty(name="Use Deform", default=True)

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}

        if self.use_deform:
            pick = {b.name for b in armature.data.bones if b.use_deform}
        else:
            pick = {b.name for b in armature.data.bones if not b.use_deform}

        bone_selection.select_bones_by_name_set(context, armature, pick)

        self.report({"INFO"}, "Selection updated by deform state.")
        return {"FINISHED"}


classes = (
    RIGPANEL_OT_set_deform,
    RIGPANEL_OT_select_by_deform,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
