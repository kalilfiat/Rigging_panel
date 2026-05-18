import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from ..utils import context as rig_context


class RIGPANEL_OT_set_pose_position(Operator):
    bl_idname = "rigpanel.set_pose_position"
    bl_label = "Set Pose Position"
    bl_options = {"REGISTER", "UNDO"}

    position: EnumProperty(
        name="Position",
        items=(
            ("POSE", "Pose Position", ""),
            ("REST", "Rest Position", ""),
        ),
    )

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        armature.data.pose_position = self.position
        return {"FINISHED"}


classes = (RIGPANEL_OT_set_pose_position,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
