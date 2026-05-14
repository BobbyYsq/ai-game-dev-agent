---
name: visual-clarity-fix
description: Keep Godot lighting, camera, materials, WorldEnvironment, and post-processing clear and readable. Use for post effects, lighting adjustment, visibility, clarity, exposure, glow, fog, DOF, blur, darkness, or overexposure tasks.
when_to_use: Use before any Hastur Godot task that adjusts lighting, camera, environment, material visibility, or post-processing, especially when the expected result is a clearer prototype/editor preview rather than a cinematic effect.
user-invocable: true
---

## Required workflow

Apply this skill before generating or repairing Hastur GDScript for the matching task.

1. Prioritize a clear editor/game preview over cinematic mood unless the user explicitly asks for the exact cinematic effect.
2. Do not make the scene darker, blurrier, foggier, or more overexposed than before.
3. Avoid enabling depth of field blur, fog, volumetric fog, high glow/bloom, heavy SSAO, aggressive color grading, auto exposure, or very dark backgrounds by default.
4. If the user asks to improve visibility or clarity, first disable or neutralize blur, fog, excessive glow, auto exposure, and extreme exposure before adding new effects.
5. Prefer conservative defaults:
   - `WorldEnvironment.environment.ambient_light_energy`: about `0.6` to `1.2`.
   - `Environment.background_energy_multiplier`: about `0.8` to `1.2`.
   - `Environment.tonemap_exposure`: about `0.8` to `1.1`.
   - Camera attributes: `auto_exposure_enabled=false`, `dof_blur_near_enabled=false`, `dof_blur_far_enabled=false`.
   - `DirectionalLight3D.light_energy`: about `0.7` to `1.5`.
6. Save the edited scene/resource when appropriate.

## Required output contract

The Hastur result must call `executeContext.output("result", text)` with concise before/after evidence under 700 characters:

- Environment/background energy.
- Exposure or tonemap values.
- Glow/fog/DOF/auto exposure state.
- Main light energy.
- Camera distance or framing if changed.
- Save status.
