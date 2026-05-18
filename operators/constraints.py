import bpy
from bpy.props import BoolProperty
from bpy.types import Operator

from ..utils import context as rig_context


def _copy_constraint(source_constraint, target_pose_bone):
    new_constraint = target_pose_bone.constraints.new(type=source_constraint.type)
    new_constraint.name = source_constraint.name

    for prop in source_constraint.bl_rna.properties:
        if prop.identifier in {"rna_type", "type", "name"} or prop.is_readonly:
            continue
        try:
            setattr(new_constraint, prop.identifier, getattr(source_constraint, prop.identifier))
        except (AttributeError, TypeError, ValueError):
            pass

    return new_constraint


class RIGPANEL_OT_copy_constraints(Operator):
    bl_idname = "rigpanel.copy_constraints"
    bl_label = "Copy Constraints"
    bl_options = {"REGISTER", "UNDO"}

    replace_existing: BoolProperty(name="Replace Existing", default=False)

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        if context.mode != "POSE":
            bpy.ops.object.mode_set(mode="POSE")

        active = rig_context.active_pose_bone(context)
        names = rig_context.require_selected_bones(self, context)
        if not names:
            return {"CANCELLED"}
        if active is None:
            self.report({"WARNING"}, "Use Pose Mode with an active source bone.")
            return {"CANCELLED"}

        targets = [bone for bone in rig_context.pose_bones_from_names(armature, names) if bone.name != active.name]
        if not targets:
            self.report({"WARNING"}, "Select at least one target bone besides the active bone.")
            return {"CANCELLED"}

        for target in targets:
            if self.replace_existing:
                for constraint in list(target.constraints):
                    target.constraints.remove(constraint)
            for constraint in active.constraints:
                _copy_constraint(constraint, target)

        self.report({"INFO"}, f"Copied constraints to {len(targets)} bone(s).")
        return {"FINISHED"}


class RIGPANEL_OT_set_constraints_state(Operator):
    bl_idname = "rigpanel.set_constraints_state"
    bl_label = "Mute Constraints"
    bl_options = {"REGISTER", "UNDO"}

    mute: BoolProperty(name="Mute", default=False)

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}
        if context.mode != "POSE":
            bpy.ops.object.mode_set(mode="POSE")

        names = rig_context.require_selected_bones(self, context)
        if not names:
            return {"CANCELLED"}

        changed = 0
        for pose_bone in rig_context.pose_bones_from_names(armature, names):
            for constraint in pose_bone.constraints:
                constraint.mute = self.mute
                changed += 1

        self.report({"INFO"}, f"Updated {changed} constraint(s).")
        return {"FINISHED"}


classes = (
    RIGPANEL_OT_copy_constraints,
    RIGPANEL_OT_set_constraints_state,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
