# Exercise catalogue data contract

**Status:** specification only; a complete validated catalogue is not yet implemented.

The catalogue must distinguish an exercise from a media link and from a substitution recommendation. Sharing a target muscle is not sufficient evidence of equivalence.

## Exercise entity

Required fields:
- `exercise_id`: stable internal identifier.
- `canonical_name`: normalized display name.
- `aliases`: known naming variants.
- `primary_muscles` and `secondary_muscles`: controlled identifiers.
- `movement_pattern`: controlled value (for example horizontal_push, vertical_pull, knee_dominant, hip_hinge, elbow_flexion, elbow_extension, plantar_flexion, trunk_flexion).
- `equipment`: one or more controlled equipment identifiers.
- `laterality`: bilateral, unilateral, alternating, or not_applicable.
- `resistance_profile`: free_weight, machine, cable, bodyweight, band, or mixed.
- `skill_level` and `safety_notes`.

## Media entity

Media is stored separately and includes `media_id`, `exercise_id`, `source_name`, `source_url`, `variation_demonstrated`, `verification_status`, `verified_at`, `verified_by`, and optional locally stored thumbnail path. Never mark a video verified merely because its title resembles the exercise name.

## Substitution relationship

A substitution is a directed, evidence-bearing relationship with:
- source exercise and candidate exercise IDs;
- equivalence dimensions (movement pattern, target muscles, joint actions, equipment, stability demand, range of motion);
- material differences and contraindications;
- evidence/source and reviewer;
- status: proposed, reviewed, approved, rejected.

The engine must not rank exercises as interchangeable solely by muscle group. If evidence is insufficient, label the option as an alternative rather than an equivalent. User safety constraints and available equipment take precedence.

## Data quality rules

- Unknown fields remain unknown; do not infer them from a video thumbnail.
- Preserve the original source terminology alongside normalized fields.
- Do not bundle proprietary course material in public releases without permission.
- Require review before an exercise relationship becomes an automatic substitution.
