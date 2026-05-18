import math

from . import context as rig_context


def _nearly_equal(a, b, tolerance=0.0001):
    return math.isclose(a, b, abs_tol=tolerance)


def _constraint_invalid(constraint):
    return hasattr(constraint, "is_valid") and constraint.is_valid is False


def _parse_name_list(text):
    return {part.strip() for part in text.split(",") if part.strip()}


def _is_allowed_root_bone(bone_name, settings):
    allowed = _parse_name_list(settings.debug_root_names)
    allowed_lower = {name.lower() for name in allowed}
    return bone_name in allowed or bone_name.lower() in allowed_lower


def bones_without_parent(armature, settings):
    """Bones with no parent, excluding expected rig root(s)."""
    roots = [bone for bone in armature.data.bones if bone.parent is None]
    if not roots:
        return []

    if not settings.debug_exclude_root_bones:
        return [bone.name for bone in roots]

    if len(roots) == 1:
        return []

    orphans = [
        bone.name
        for bone in roots
        if not _is_allowed_root_bone(bone.name, settings)
    ]
    return orphans


def gather_validation(armature, settings, check="ALL"):
    """Return list of dicts: id, title, bone_names (list), message (optional str)."""
    groups = []

    if check in {"NO_DEFORM", "ALL"}:
        names = [bone.name for bone in armature.data.bones if not bone.use_deform]
        if names:
            groups.append({
                "id": "NO_DEFORM",
                "title": "Without deform",
                "bone_names": names,
            })

    if check in {"NO_PARENT", "ALL"}:
        names = bones_without_parent(armature, settings)
        if names:
            groups.append({
                "id": "NO_PARENT",
                "title": "Without parent (orphan)",
                "bone_names": names,
            })

    if check in {"CONSTRAINT_ERRORS", "ALL"}:
        names = []
        for pose_bone in armature.pose.bones:
            if any(_constraint_invalid(c) for c in pose_bone.constraints):
                names.append(pose_bone.name)
        if names:
            groups.append({
                "id": "CONSTRAINT_ERRORS",
                "title": "Invalid constraints",
                "bone_names": sorted(set(names)),
            })

    if check in {"ARMATURE_SCALE", "ALL"}:
        if any(not _nearly_equal(value, 1.0) for value in armature.scale):
            groups.append({
                "id": "ARMATURE_SCALE",
                "title": "Armature scale",
                "bone_names": [],
                "message": "Object scale is not (1, 1, 1). Apply scale with Ctrl+A.",
            })

    if check in {"NON_UNIFORM_SCALE", "ALL"}:
        sx, sy, sz = armature.scale
        if not (_nearly_equal(sx, sy) and _nearly_equal(sy, sz)):
            groups.append({
                "id": "NON_UNIFORM_SCALE",
                "title": "Non-uniform scale",
                "bone_names": [],
                "message": "Armature has non-uniform scale on X/Y/Z.",
            })

    return groups


def store_report(context, groups):
    settings = rig_context.get_settings(context)
    settings.validation_groups.clear()

    for data in groups:
        group = settings.validation_groups.add()
        group.category_id = data["id"]
        group.title = data["title"]
        group.message = data.get("message", "")
        group.bone_names_csv = ",".join(data.get("bone_names", []))


def bone_names_for_category(settings, category_id):
    for group in settings.validation_groups:
        if group.category_id == category_id and group.bone_names_csv:
            return [n for n in group.bone_names_csv.split(",") if n]
    return []


def all_report_bone_names(settings):
    names = set()
    for group in settings.validation_groups:
        names.update(bone_names_for_category(settings, group.category_id))
    return names
