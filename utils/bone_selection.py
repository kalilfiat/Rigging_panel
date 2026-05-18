"""
Bone selection for Blender 5.x+.

`bpy.types.Bone` (elements of `armature.data.bones`) no longer exposes `.select`.
Use `PoseBone.select` in Pose Mode or `EditBone.select` (+ head/tail) in Edit Armature.
"""

import bpy


def select_bones_by_name_set(context, armature, name_set):
    """Select only bones whose names are in ``name_set``; deselect all others."""
    if armature is None:
        return

    armature.select_set(True)
    context.view_layer.objects.active = armature

    mode = context.mode
    if mode == "EDIT_ARMATURE":
        for edit_bone in armature.data.edit_bones:
            selected = edit_bone.name in name_set
            edit_bone.select = selected
            edit_bone.select_head = selected
            edit_bone.select_tail = selected
        return

    if mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")

    for pose_bone in armature.pose.bones:
        pose_bone.select = pose_bone.name in name_set
