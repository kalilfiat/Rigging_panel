import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Operator

from ..utils import bone_selection
from ..utils import context as rig_context
from ..utils import validation_data
from ..utils.validation_ui import draw_validation_report


def _run_validation(context, check):
    armature = rig_context.require_armature(None, context)
    if not armature:
        return None

    settings = rig_context.get_settings(context)
    groups = validation_data.gather_validation(armature, settings, check)
    validation_data.store_report(context, groups)

    if not groups:
        settings.validation_summary = "No issues found."
        return groups

    parts = []
    for group in groups:
        if group.get("bone_names"):
            parts.append(f"{group['title']}: {len(group['bone_names'])}")
        else:
            parts.append(group["title"])
    settings.validation_summary = "; ".join(parts)
    return groups


class RIGPANEL_OT_validate_rig(Operator):
    bl_idname = "rigpanel.validate_rig"
    bl_label = "Validate Rig"
    bl_options = {"REGISTER"}

    check: EnumProperty(
        name="Check",
        items=(
            ("NO_DEFORM", "Bones Without Deform", ""),
            ("CONSTRAINT_ERRORS", "Constraint Errors", ""),
            ("NO_PARENT", "Bones Without Parent", ""),
            ("ARMATURE_SCALE", "Armature Scale", ""),
            ("NON_UNIFORM_SCALE", "Non-Uniform Scale", ""),
            ("ALL", "All Checks", ""),
        ),
        default="ALL",
    )
    open_report: BoolProperty(
        name="Open Report",
        description="Open the validation report popup when issues are found",
        default=True,
    )

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}

        groups = _run_validation(context, self.check)

        if not groups:
            self.report({"INFO"}, rig_context.get_settings(context).validation_summary)
            return {"FINISHED"}

        self.report({"WARNING"}, rig_context.get_settings(context).validation_summary)

        if self.open_report:
            bpy.ops.rigpanel.show_validation_report("INVOKE_DEFAULT")

        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}


class RIGPANEL_OT_show_validation_report(Operator):
    bl_idname = "rigpanel.show_validation_report"
    bl_label = "Validation Report"
    bl_options = {"REGISTER"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=360)

    def draw(self, context):
        draw_validation_report(self.layout, context)

    def execute(self, context):
        return {"FINISHED"}


class RIGPANEL_OT_clear_validation_report(Operator):
    bl_idname = "rigpanel.clear_validation_report"
    bl_label = "Clear Report"
    bl_options = {"REGISTER"}

    def execute(self, context):
        settings = rig_context.get_settings(context)
        settings.validation_groups.clear()
        settings.validation_summary = ""
        self.report({"INFO"}, "Validation report cleared.")
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}


class RIGPANEL_OT_select_validation_result(Operator):
    bl_idname = "rigpanel.select_validation_result"
    bl_label = "Select Validation Result"
    bl_options = {"REGISTER", "UNDO"}

    target: EnumProperty(
        name="Target",
        items=(
            ("NO_DEFORM", "Bones Without Deform", ""),
            ("NO_PARENT", "Bones Without Parent", ""),
            ("CONSTRAINT_ERRORS", "Bones With Constraint Errors", ""),
        ),
    )

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}

        settings = rig_context.get_settings(context)
        names = validation_data.bone_names_for_category(settings, self.target)
        if not names:
            groups = validation_data.gather_validation(armature, settings, self.target)
            for group in groups:
                if group["id"] == self.target:
                    names = group.get("bone_names", [])
                    break

        if not names:
            self.report({"INFO"}, "No bones for this category.")
            return {"CANCELLED"}

        bone_selection.select_bones_by_name_set(context, armature, set(names))
        self.report({"INFO"}, f"Selected {len(names)} bone(s).")
        return {"FINISHED"}


class RIGPANEL_OT_select_validation_group(Operator):
    bl_idname = "rigpanel.select_validation_group"
    bl_label = "Select Group"
    bl_options = {"REGISTER", "UNDO"}

    category_id: StringProperty(name="Category")

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}

        settings = rig_context.get_settings(context)
        names = validation_data.bone_names_for_category(settings, self.category_id)
        if not names:
            self.report({"INFO"}, "No bones in this group.")
            return {"CANCELLED"}

        bone_selection.select_bones_by_name_set(context, armature, set(names))
        self.report({"INFO"}, f"Selected {len(names)} bone(s).")
        return {"FINISHED"}


class RIGPANEL_OT_select_validation_bone(Operator):
    bl_idname = "rigpanel.select_validation_bone"
    bl_label = "Select Bone"
    bl_options = {"REGISTER", "UNDO"}

    bone_name: StringProperty(name="Bone")

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature or not self.bone_name:
            return {"CANCELLED"}

        bone_selection.select_bones_by_name_set(context, armature, {self.bone_name})
        self.report({"INFO"}, f"Selected {self.bone_name}.")
        return {"FINISHED"}


class RIGPANEL_OT_select_all_validation_bones(Operator):
    bl_idname = "rigpanel.select_all_validation_bones"
    bl_label = "Select All Reported Bones"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        armature = rig_context.require_armature(self, context)
        if not armature:
            return {"CANCELLED"}

        settings = rig_context.get_settings(context)
        names = validation_data.all_report_bone_names(settings)
        if not names:
            self.report({"INFO"}, "Run validation first.")
            return {"CANCELLED"}

        bone_selection.select_bones_by_name_set(context, armature, names)
        self.report({"INFO"}, f"Selected {len(names)} bone(s).")
        return {"FINISHED"}


classes = (
    RIGPANEL_OT_validate_rig,
    RIGPANEL_OT_show_validation_report,
    RIGPANEL_OT_clear_validation_report,
    RIGPANEL_OT_select_validation_result,
    RIGPANEL_OT_select_validation_group,
    RIGPANEL_OT_select_validation_bone,
    RIGPANEL_OT_select_all_validation_bones,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
