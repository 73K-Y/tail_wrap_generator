# Tail Wrap Generator

A Blender add-on (Python) that generates procedural cable/tail wraps along a mesh surface using guide circles and shrinkwrap projection.

**Blender 5.0+ · Python 3.11+**

---

## Features

- Place START and END guide circles to define wrap path
- Distribute N lines evenly between guides
- Project lines onto any target mesh via `closest_point_on_mesh` (world ↔ local space conversion handled automatically)
- Bezier spline output with configurable thickness and offset
- Per-vertex color attributes for guide highlighting (Blender 4.0+ API)

---

## Installation

1. Download `tail_wrap_generator.py`
2. Open Blender → **Edit > Preferences > Add-ons > Install**
3. Select the `.py` file and enable the add-on
4. Find the panel in **View3D > Sidebar > Tail Wrap**

---

## Usage

1. **Create Guides** — click *Create Tail Guides* to spawn START and END circles
2. Move/scale the guides to define start and end of the wrap
3. Set your **Target Mesh** (the surface lines will project onto)
4. Adjust **Lines**, **Segments**, **Thickness**, **Offset**
5. Click **Generate Tail Lines**

---

## Parameters

| Parameter | Default | Description |
|---|---|---|
| Lines | 8 | Number of individual cables |
| Segments | 10 | Bezier control points per cable |
| Thickness | 0.02 | Bevel depth of each curve |
| Shrink Offset | 0.05 | Outward offset from mesh surface |
| Target Mesh | — | Mesh object to project onto |
| Top Color | Red | Guide vertex color above Z=0 |
| Bottom Color | Green | Guide vertex color below Z=0 |

---

## Requirements

- Blender 5.0 or higher (uses `color_attributes` API — not compatible with Blender < 4.0)
- No external Python dependencies

---

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting policy.  
Dependency updates are managed automatically via [Dependabot](.github/dependabot.yml).

---

## License

MIT License — see [LICENSE](LICENSE) for details.
