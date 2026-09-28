# automationTypes — Robot / Mechanism Schema

`RobotConfig.py` (`foundationTypes/automationTypes/`) is generated from a recursive, compositional JSON Schema for describing robots and robotic mechanisms. Schema source: [`schema/schemas/Robot/`](../schema/schemas/Robot/), entry point [`robot-mechanism.schema.json`](../schema/schemas/Robot/robot-mechanism.schema.json) (JSON Schema Draft 2020-12).

This page documents the schema for end use — authoring a mechanism/robot JSON document, or reading the generated Python. For the codegen pipeline mechanics, see [`.claude/specs/schemaCodegen.md`](../.claude/specs/schemaCodegen.md); this schema's generation is a known partial exception to that pipeline's fidelity guarantees (see the last section below).

## What this models

A `MechanismDefinition` describes kinematic **structure** — bodies, joints, constraints, and how simpler mechanisms compose into more complex ones — not a fixed catalog of robot types. There is no `"stewart"` or `"scara"` field anywhere in this schema. A Stewart platform, a SCARA arm, a gimbal, and a six-axis manipulator are all just `MechanismDefinition` objects; what makes one a "Stewart platform" is its `bodies`/`joints`/`constraints` plus a `classification.tags` hint for humans and tooling, never a structural schema branch. This is deliberate: it means the schema doesn't need to grow a new top-level type every time someone invents a new mechanism architecture.

The other deliberate property is **recursion**: a mechanism can be built out of other mechanisms (`components`), and those can be built out of others, with no depth limit enforced by the schema.

## Directory layout

Each file is one reusable concept, referenced by relative `$ref` from wherever it's used. Folders group concepts the way the schema itself separates them:

| Folder | Concepts | Notes |
|---|---|---|
| `Common/` | `Id` | The stable string identifier used everywhere (bodies, joints, mechanisms, ...). Not a UUID — see below. |
| `Units/` | `Unit`, `Quantity`, `Units` | The unit system. `Quantity` is a bare number or `{value, unit}`. |
| `Geometry/` | `Vector3`, `Vector6`, `Quaternion`, `RotationMatrix`, `AxisAngle`, `RPY`, `Rotation`, `Transform` | Reusable pose primitives. |
| `Mechanism/` | `Classification`, `MechanismDefinition` | The recursive root object and its descriptive (non-structural) classification. |
| `Structure/` | `Body`, `Frame` | Rigid bodies and the frames attached to them. |
| `Joints/` | `JointCoordinate`, `JointLimits`, `JointBase`, `Joint` | Kinematic joints, revolute through fixed. |
| `Constraints/` | `Constraint` | Generic loop-closure / coincidence / etc. constraints for parallel and closed-chain mechanisms. |
| `Composition/` | `Interface`, `Connection`, `Component` | How mechanisms mount onto each other. |
| `Kinematics/` | `VariableReference`, `DHValue`, `DHParameter`, `KinematicRepresentationBase`, `KinematicRepresentation`, `Kinematics` | DH / PoE / constraint-based descriptions of a mechanism's kinematics. |

## Core concepts

### Identity (`id`)

Every `Body`/`Joint`/`Constraint`/`Component`/`Connection`/`MechanismDefinition` has a required `id`: a stable string matching `^[A-Za-z_][A-Za-z0-9_-]*$` (e.g. `"link_1"`, `"six_axis"`), **not a UUID**. IDs need to be human-readable so they can be referenced by name elsewhere in the same document (a joint's `parent`/`child`, a component's `definition`, a connection's `parent`/`child`). Uniqueness is your application's responsibility — the schema doesn't enforce it globally.

`MechanismDefinition` also carries `robot_type` (`ur` / `obsbot` / `brooksPrecisionFlex`, required alongside `id`), identifying the underlying robot/supplier grouping a definition describes.

### Classification is descriptive, not structural

`classification.topology` (`open_chain` / `closed_chain` / `parallel` / `hybrid` / `composite`), `.architecture`, `.functions`, and `.tags` describe a mechanism for humans and search/filtering tools. None of them gate which of `bodies`/`joints`/`constraints`/`components` you're allowed to use — a gimbal is just `classification.tags: ["gimbal"]` on an ordinary 3-joint open chain.

### Joints

Every joint has `id`, `type`, `parent`, `child`, and optionally `coordinates` (its generalized coordinates) and `metadata`. The recognized `type` values add their own fields:

| `type` | Adds |
|---|---|
| `revolute` | `axis`, `limits` |
| `prismatic` | `axis`, `limits` |
| `helical` | `axis`, `pitch` (both required), `limits` |
| `spherical`, `universal`, `planar` | `dof`, `axes`, `limits` (array, one per axis) |
| `fixed` | `transform` |

A joint `type` outside this list is still valid — it just doesn't get any type-specific fields validated; put custom data in `metadata`.

### Constraints and parallel mechanisms

A parallel or closed-chain mechanism doesn't get its own joint topology — it's built from ordinary joints plus explicit `Constraint` objects (`type: "loop_closure"` is the common case, but `type` is an open string). The schema doesn't evaluate whether the constraints are kinematically valid; it only describes them.

### Composition (`components`)

A `Component` instantiates another mechanism inside this one. `definition` is either:

- a string `id` referencing a mechanism defined elsewhere (lets the same definition be instantiated more than once — e.g. two arms sharing one `"six_axis"` definition — without duplicating it), or
- a `MechanismDefinition` nested inline.

`Interface`s (named, pointing at a frame) and `Connection`s (linking one component's interface to another's) are how components actually mount together, so a child mechanism never has to know in advance what it will be mounted on.

### Kinematics representations

`kinematics.representations` is a list — a mechanism can carry more than one representation at once. Recognized `type`s:

- `dh` / `modified_dh` — `parameters`: a list of `DHParameter` (`a`, `alpha`, `d`, `theta`), each either a constant `Quantity` or `{"variable": "<coordinate id>"}`.
- `poe` — `space_frame`/`body_frame`, `home_transform`, and `joints` (each a `screw_axis`: `[wx, wy, wz, vx, vy, vz]`).
- `constraint_based` — `coordinates` and `constraints`, for parallel/closed-chain mechanisms that have no single DH chain.

DH is never required and never implies "this is a serial manipulator" — it's just one way to describe a chain that happens to have one.

### Rotation is always unambiguous

`Transform.rotation` accepts exactly one of `quaternion`, `rotation_matrix` (row-major), `axis_angle`, or `rpy` (with an explicit `convention`) — never more than one at a time, and never a bare set of numbers with an implied convention.

## Worked example

A minimal two-link revolute arm:

```json
{
  "id": "two_link_arm",
  "robot_type": "ur",
  "classification": { "topology": "open_chain", "architecture": ["serial"] },
  "bodies": [{ "id": "link_0" }, { "id": "link_1" }, { "id": "link_2" }],
  "joints": [
    {
      "id": "joint_1",
      "type": "revolute",
      "parent": "link_0",
      "child": "link_1",
      "axis": [0, 0, 1],
      "coordinates": [{ "id": "q1", "unit": "rad" }],
      "limits": { "position": { "min": -3.14, "max": 3.14 } }
    },
    {
      "id": "joint_2",
      "type": "revolute",
      "parent": "link_1",
      "child": "link_2",
      "axis": [0, 0, 1],
      "coordinates": [{ "id": "q2", "unit": "rad" }]
    }
  ],
  "kinematics": {
    "representations": [
      {
        "type": "dh",
        "convention": "standard",
        "parameters": [
          { "joint": "joint_1", "a": 0, "alpha": 0, "d": 0, "theta": { "variable": "q1" } },
          { "joint": "joint_2", "a": 0.5, "alpha": 0, "d": 0, "theta": { "variable": "q2" } }
        ]
      }
    ]
  }
}
```

Two mechanisms composed (an arm mounted on another mechanism by reference, without duplicating the arm's definition):

```json
{
  "id": "arm_on_arm",
  "robot_type": "ur",
  "classification": { "topology": "composite", "architecture": ["serial"] },
  "components": [
    { "id": "base_arm", "kind": "submechanism", "definition": "two_link_arm" },
    { "id": "top_arm", "kind": "submechanism", "definition": "two_link_arm" }
  ],
  "connections": [
    {
      "id": "mount_top_on_base",
      "parent": "base_arm",
      "child": "top_arm",
      "parent_interface": "tool",
      "child_interface": "base"
    }
  ]
}
```

## Validating a document

This schema uses Draft 2020-12 features throughout — recursive `$ref`, `oneOf`, `if`/`then`, and `unevaluatedProperties` for extensible joint/kinematics types — so it needs a validator that actually implements 2020-12, resolving cross-file `$ref`s by each file's `$id`. `ajv-cli` (Node) and Python's `jsonschema` (with a `referencing.Registry` built from every file's `$id`) both work; a Draft-06/07-only validator will reject or silently mis-handle parts of this schema.

## The generated Python types

`schema/scripts/generateRobotConfig.sh` runs this schema through quicktype to produce `src/foundationTypes/automationTypes/RobotConfig.py`. This is a known, deliberate exception to the strict-typing/fidelity guarantees in [`.claude/specs/schemaCodegen.md`](../.claude/specs/schemaCodegen.md): **quicktype cannot represent the `if`/`then` type-specific fields**, so the generated `Joint` class only has the base fields (`id`, `type`, `parent`, `child`, `coordinates`, `metadata` — no `axis`, `limits`, `pitch`, `dof`, `axes`, or `transform`), and the generated `KinematicRepresentation` class only has `type` and `metadata` (no `parameters`, `convention`, `space_frame`, `joints`, `coordinates`, or `constraints`). Recursion itself (`Component.definition`) generates correctly. If you need the full joint/kinematics shape in Python, validate against the JSON Schema directly (see above) rather than relying on the generated dataclasses for those two types.
