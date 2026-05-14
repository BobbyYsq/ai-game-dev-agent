---
name: mesh-surface-orientation-fix
description: Fix Godot MeshInstance3D terrain, continent, map, or landmass surfaces when the front or top is transparent, the back or underside has material, material appears upside-down, normals, culling, winding, instance transparency, or backface visibility are wrong.
when_to_use: Use before any Hastur Godot task about continent, terrain, map, landmass material orientation, front or back transparency, top or underside visibility, ArrayMesh winding, normals, cull_mode, GeometryInstance3D.transparency, material_override, or backface visibility.
user-invocable: true
---

## Required workflow

Apply this skill before generating or repairing Hastur GDScript for the matching task.

1. Identify the intended target first. If the user asks about a continent, terrain, map, or landmass, do not repair incidental trees, decorations, houses, labels, or child foliage meshes.
2. Inspect the exact `MeshInstance3D`, mesh surface count, active material source, `GeometryInstance3D.material_override`, `GeometryInstance3D.transparency`, `BaseMaterial3D.cull_mode`, material transparency/alpha, and representative triangle normal or vertex/index winding.
3. Godot `ArrayMesh` triangle front faces use clockwise winding. For flat generated terrain or continent meshes, the top surface normal should generally point toward positive Y.
4. If the top/front is invisible while the underside/back is visible, treat it as a mesh winding/normal/cull/material-alpha/instance-transparency problem. Do not try to hide it with lighting, camera, post-processing, or world environment changes.
5. Prefer rebuilding or rewinding the mesh so top/front faces are actually front-facing. Also force the instance to be visible and opaque: `visible=true`, `transparency=0.0`, no unwanted `material_overlay`, opaque active material alpha `1.0`, disabled material transparency, and normal back-face culling.
6. Do not use `CULL_DISABLED` or a two-sided material as the only fix unless the user explicitly asks for a two-sided surface or the mesh cannot be rebuilt. If used temporarily, say that clearly.
7. Save the edited scene/resource when appropriate.

## Required output contract

The Hastur result must call `executeContext.output("result", text)` with concise before/after evidence under 700 characters:

- Scene-relative target path. Do not output editor-internal paths containing `@EditorNode`.
- Instance visibility/transparency state.
- Material/cull/alpha/transparency state.
- Normal or winding evidence.
- Explicit top/front visibility after the fix, using a machine-checkable field such as `top_visible=true`, `front_visible=true`, or `visible_from_above=true`.

The Before line must reproduce the actual problem. If Before already says `top_visible=true` or `front_visible=true`, you have not found the user's problem yet.

Example:

```text
Before: path=GeneratedContent/TerrainMesh inst_trans=1.00 cull=BACK alpha=1.00 normal_y=1.00 top_visible=false
After: path=GeneratedContent/TerrainMesh inst_trans=0.00 cull=BACK alpha=1.00 normal_y=1.00 winding=clockwise top_visible=true saved=true
```
