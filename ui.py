import addon_utils
import bpy
from bpy.types import Panel

from .utils import context as rig_context


def _panel_version_text():
    for mod in addon_utils.modules(refresh=False):
        info = getattr(mod, "bl_info", None)
        if info and info.get("name") == "Rigging Utility Panel":
            return ".".join(str(x) for x in info["version"])
    return "?"


def _section(layout, settings, prop_name, label, icon):
    row = layout.row(align=True)
    expanded = getattr(settings, prop_name)
    row.prop(
        settings,
        prop_name,
        text=label,
        icon="TRIA_DOWN" if expanded else "TRIA_RIGHT",
        emboss=False,
    )
    row.label(text="", icon=icon)
    return expanded


def _operator_button(layout, operator, text, icon="NONE", **props):
    op = layout.operator(operator, text=text, icon=icon)
    for key, value in props.items():
        setattr(op, key, value)
    return op


class RIGPANEL_PT_main(Panel):
    bl_label = "Rigging Utility"
    bl_idname = "RIGPANEL_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rig Tools"

    def draw(self, context):
        layout = self.layout
        settings = rig_context.get_settings(context)
        armature = rig_context.active_armature(context)
        selected_count = rig_context.selected_count(context)

        header = layout.box()
        header.label(text=f"v{_panel_version_text()} · Mode: {context.mode}", icon="ARMATURE_DATA")
        if armature:
            header.label(text=f"Armature: {armature.name}")
            header.label(text=f"Selected Bones: {selected_count}")
        else:
            header.label(text="Select an armature to use rig tools.", icon="ERROR")

        layout.separator()
        self.draw_display(layout, settings, armature)
        self.draw_shapes_colors(layout, settings)
        self.draw_constraints(layout, settings)
        self.draw_deform(layout, settings)
        self.draw_naming(layout, settings)
        self.draw_relations(layout, settings)
        self.draw_pose(layout, settings)
        self.draw_validation(layout, settings, armature)

    def draw_display(self, layout, settings, armature):
        if not _section(layout, settings, "show_display", "Display", "HIDE_OFF"):
            return
        box = layout.box()
        row = box.row(align=True)
        _operator_button(row, "rigpanel.toggle_armature_display", "In Front", "XRAY", target="IN_FRONT")
        _operator_button(row, "rigpanel.toggle_armature_display", "Axes", "EMPTY_AXIS", target="AXES")
        _operator_button(row, "rigpanel.toggle_armature_display", "Names", "SORTALPHA", target="NAMES")

        grid = box.grid_flow(columns=2, even_columns=True, align=True)
        for display_type, label in (
            ("OCTAHEDRAL", "Octa"),
            ("STICK", "Stick"),
            ("BBONE", "B-Bone"),
            ("ENVELOPE", "Envelope"),
            ("WIRE", "Wire"),
        ):
            _operator_button(grid, "rigpanel.set_display_type", label, display_type=display_type)

        _operator_button(box, "rigpanel.reveal_bones", "Reveal / Unhide All", "HIDE_OFF")
        _operator_button(box, "rigpanel.toggle_weight_overlay", "Weight Overlay", "WPAINT_HLT")

    def draw_shapes_colors(self, layout, settings):
        if not _section(layout, settings, "show_shapes_colors", "Custom Shapes & Colors", "COLOR"):
            return
        box = layout.box()
        row = box.row(align=True)
        row.prop(settings, "custom_shape_object", text="")
        _operator_button(row, "rigpanel.pick_custom_shape", "Pick", "EYEDROPPER")
        row = box.row(align=True)
        _operator_button(row, "rigpanel.apply_custom_shape", "Apply Shape", "OBJECT_DATA")
        _operator_button(row, "rigpanel.clear_custom_shape", "Clear", "X")

        box.prop(settings, "color", text="Color")
        row = box.row(align=True)
        op = _operator_button(row, "rigpanel.apply_bone_color", "Edit", "BONE_DATA", apply_to="EDIT")
        op.color = tuple(settings.color)
        op = _operator_button(row, "rigpanel.apply_bone_color", "Pose", "POSE_HLT", apply_to="POSE")
        op.color = tuple(settings.color)
        op = _operator_button(row, "rigpanel.apply_bone_color", "Both", "LINKED", apply_to="BOTH")
        op.color = tuple(settings.color)

    def draw_constraints(self, layout, settings):
        if not _section(layout, settings, "show_constraints", "Constraints", "CONSTRAINT_BONE"):
            return
        box = layout.box()
        row = box.row(align=True)
        _operator_button(row, "rigpanel.copy_constraints", "Copy", "COPYDOWN", replace_existing=False)
        _operator_button(row, "rigpanel.copy_constraints", "Replace", "DUPLICATE", replace_existing=True)
        row = box.row(align=True)
        _operator_button(row, "rigpanel.set_constraints_state", "Mute", "HIDE_ON", mute=True)
        _operator_button(row, "rigpanel.set_constraints_state", "Unmute", "HIDE_OFF", mute=False)

    def draw_deform(self, layout, settings):
        if not _section(layout, settings, "show_deform", "Deform", "MOD_ARMATURE"):
            return
        box = layout.box()
        row = box.row(align=True)
        _operator_button(row, "rigpanel.set_deform", "Deform On", "CHECKMARK", use_deform=True)
        _operator_button(row, "rigpanel.set_deform", "Deform Off", "CANCEL", use_deform=False)
        row = box.row(align=True)
        _operator_button(row, "rigpanel.select_by_deform", "Select Deform", "RESTRICT_SELECT_OFF", use_deform=True)
        _operator_button(row, "rigpanel.select_by_deform", "Select Non-Deform", "RESTRICT_SELECT_OFF", use_deform=False)

    def draw_naming(self, layout, settings):
        if not _section(layout, settings, "show_naming", "Naming", "SORTALPHA"):
            return
        box = layout.box()
        row = box.row(align=True)
        row.prop(settings, "name_prefix", text="Prefix")
        op = _operator_button(row, "rigpanel.apply_name_prefix", "Apply", "SORTALPHA")
        op.prefix = settings.name_prefix
        row = box.row(align=True)
        row.prop(settings, "name_suffix", text="Suffix")
        op = _operator_button(row, "rigpanel.apply_name_suffix", "Apply", "SORTALPHA")
        op.suffix = settings.name_suffix
        row = box.row(align=True)
        op = _operator_button(row, "rigpanel.apply_full_bone_name", "Prefix + Suffix", "FILE_PARENT")
        op.prefix = settings.name_prefix
        op.suffix = settings.name_suffix
        grid = box.grid_flow(columns=3, even_columns=True, align=True)
        for suffix in (".L", ".R", "_L", "_R", "-L", "-R"):
            _operator_button(grid, "rigpanel.apply_name_suffix", suffix, suffix=suffix)

    def draw_relations(self, layout, settings):
        if not _section(layout, settings, "show_relations", "Bone Relations", "BONE_DATA"):
            return
        box = layout.box()
        row = box.row(align=True)
        _operator_button(row, "rigpanel.clear_bone_parent", "Clear Parent", "UNLINKED")
        _operator_button(row, "rigpanel.flip_head_tail", "Head Tail Flip", "ARROW_LEFTRIGHT")

    def draw_pose(self, layout, settings):
        if not _section(layout, settings, "show_pose", "Pose", "POSE_HLT"):
            return
        box = layout.box()
        row = box.row(align=True)
        _operator_button(row, "rigpanel.set_pose_position", "Pose", "POSE_HLT", position="POSE")
        _operator_button(row, "rigpanel.set_pose_position", "Rest", "ARMATURE_DATA", position="REST")

    def draw_validation(self, layout, settings, armature):
        if not _section(layout, settings, "show_validation", "Validation / Debug", "ERROR"):
            return
        box = layout.box()
        box.prop(settings, "debug_exclude_root_bones", text="Ignore Rig Root")
        if settings.debug_exclude_root_bones:
            box.prop(settings, "debug_root_names", text="Root Names")

        _operator_button(box, "rigpanel.validate_rig", "Run All Checks", "CHECKMARK", check="ALL")

        grid = box.grid_flow(columns=2, even_columns=True, align=True)
        _operator_button(grid, "rigpanel.validate_rig", "No Deform", "BONE_DATA", check="NO_DEFORM")
        _operator_button(grid, "rigpanel.validate_rig", "No Parent", "OUTLINER", check="NO_PARENT")
        _operator_button(grid, "rigpanel.validate_rig", "Constraints", "CONSTRAINT_BONE", check="CONSTRAINT_ERRORS")
        _operator_button(grid, "rigpanel.validate_rig", "Scale", "OBJECT_ORIGIN", check="ARMATURE_SCALE")

        if settings.validation_summary:
            row = box.row(align=True)
            icon = "INFO" if settings.validation_groups else "CHECKMARK"
            row.label(text=settings.validation_summary, icon=icon)

        if settings.validation_groups:
            row = box.row(align=True)
            _operator_button(row, "rigpanel.show_validation_report", "View Report", "ZOOM_ALL")
            _operator_button(row, "rigpanel.clear_validation_report", "Clear", "X")


classes = (RIGPANEL_PT_main,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
