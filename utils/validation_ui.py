"""Shared UI drawing for the validation report popup."""

from . import context as rig_context


def draw_validation_report(layout, context):
    settings = rig_context.get_settings(context)
    layout.label(text="Validation Report", icon="ERROR")

    if settings.validation_summary:
        layout.label(text=settings.validation_summary, icon="INFO")

    if not settings.validation_groups:
        layout.label(text="No issues in the last report.", icon="CHECKMARK")
        return

    layout.operator("rigpanel.select_all_validation_bones", text="Select All Listed", icon="RESTRICT_SELECT_ON")
    layout.separator()

    for group in settings.validation_groups:
        box = layout.box()
        row = box.row(align=True)
        row.label(text=group.title, icon="ERROR")
        if group.bone_names_csv:
            op = row.operator("rigpanel.select_validation_group", text="Select All", icon="RESTRICT_SELECT_OFF")
            op.category_id = group.category_id

        if group.message:
            box.label(text=group.message, icon="BLANK1")

        if not group.bone_names_csv:
            continue

        names = [name for name in group.bone_names_csv.split(",") if name]
        col = box.column(align=True)
        for bone_name in names:
            row = col.row(align=True)
            row.label(text=bone_name)
            op = row.operator("rigpanel.select_validation_bone", text="", icon="RESTRICT_SELECT_OFF")
            op.bone_name = bone_name
