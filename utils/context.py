import bpy
from bpy.props import BoolProperty, CollectionProperty, FloatVectorProperty, PointerProperty, StringProperty
from bpy.types import PropertyGroup


SECTION_DEFAULTS = {
    "show_display": True,
    "show_shapes_colors": True,
    "show_constraints": True,
    "show_deform": True,
    "show_naming": False,
    "show_relations": False,
    "show_pose": True,
    "show_validation": True,
}


class RIGPANEL_PG_validation_group(PropertyGroup):
    category_id: StringProperty(name="Category")
    title: StringProperty(name="Title")
    message: StringProperty(name="Message")
    bone_names_csv: StringProperty(name="Bones")


class RIGPANEL_PG_settings(PropertyGroup):
    show_display: BoolProperty(name="Display", default=SECTION_DEFAULTS["show_display"])
    show_shapes_colors: BoolProperty(name="Custom Shapes & Colors", default=SECTION_DEFAULTS["show_shapes_colors"])
    show_constraints: BoolProperty(name="Constraints", default=SECTION_DEFAULTS["show_constraints"])
    show_deform: BoolProperty(name="Deform", default=SECTION_DEFAULTS["show_deform"])
    show_naming: BoolProperty(name="Naming", default=SECTION_DEFAULTS["show_naming"])
    show_relations: BoolProperty(name="Bone Relations", default=SECTION_DEFAULTS["show_relations"])
    show_pose: BoolProperty(name="Pose", default=SECTION_DEFAULTS["show_pose"])
    show_validation: BoolProperty(name="Validation / Debug", default=SECTION_DEFAULTS["show_validation"])

    custom_shape_object: StringProperty(name="Shape Object")
    name_prefix: StringProperty(name="Prefix", default="")
    name_suffix: StringProperty(name="Suffix", default=".L")
    color: FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=3,
        min=0.0,
        max=1.0,
        default=(0.25, 0.55, 1.0),
    )

    debug_exclude_root_bones: BoolProperty(
        name="Ignore Rig Root",
        description="Exclude a single root bone or names listed below from orphan check",
        default=True,
    )
    debug_root_names: StringProperty(
        name="Root Bone Names",
        description="Comma-separated root names to ignore when multiple bones have no parent",
        default="root,pelvis,Root,Pelvis,ROOT,hips,Hips",
    )

    validation_groups: CollectionProperty(type=RIGPANEL_PG_validation_group)
    validation_summary: StringProperty(name="Summary", default="")


def get_settings(context):
    return context.scene.rig_panel_settings


def active_armature(context):
    obj = context.object
    if obj and obj.type == "ARMATURE":
        return obj
    for obj in context.selected_objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def activate_armature(context, armature):
    if armature is None:
        return False
    armature.select_set(True)
    context.view_layer.objects.active = armature
    return True


def selected_pose_bones(context):
    bones = getattr(context, "selected_pose_bones", None)
    return list(bones or [])


def active_pose_bone(context):
    return getattr(context, "active_pose_bone", None)


def selected_edit_bones(context):
    bones = getattr(context, "selected_editable_bones", None)
    if bones is None:
        bones = getattr(context, "selected_bones", None)
    return list(bones or [])


def selected_data_bones(context):
    armature = active_armature(context)
    if not armature:
        return []
    if context.mode == "POSE":
        return [pose_bone.bone for pose_bone in armature.pose.bones if pose_bone.select]
    return []


def selected_bone_names(context):
    if context.mode == "POSE":
        return [bone.name for bone in selected_pose_bones(context)]
    if context.mode == "EDIT_ARMATURE":
        return [bone.name for bone in selected_edit_bones(context)]
    return [bone.name for bone in selected_data_bones(context)]


def selected_pose_or_data_bones(context):
    if context.mode == "POSE":
        return selected_pose_bones(context)
    return selected_data_bones(context)


def require_armature(operator, context):
    armature = active_armature(context)
    if armature is None:
        operator.report({"WARNING"}, "Select an armature first.")
        return None
    activate_armature(context, armature)
    return armature


def require_pose_or_edit_mode(operator, context):
    if context.mode not in {"POSE", "EDIT_ARMATURE"}:
        operator.report({"WARNING"}, "Switch to Pose Mode or Edit Armature mode.")
        return False
    return True


def require_selected_bones(operator, context):
    names = selected_bone_names(context)
    if not names:
        operator.report({"WARNING"}, "Select one or more bones first.")
        return []
    return names


def pose_bones_from_names(armature, names):
    return [armature.pose.bones[name] for name in names if name in armature.pose.bones]


def data_bones_from_names(armature, names):
    return [armature.data.bones[name] for name in names if name in armature.data.bones]


def selected_count(context):
    return len(selected_bone_names(context))


classes = (
    RIGPANEL_PG_validation_group,
    RIGPANEL_PG_settings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rig_panel_settings = PointerProperty(type=RIGPANEL_PG_settings)


def unregister():
    del bpy.types.Scene.rig_panel_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
