---
spec: DataModelHelper
scope: project
status: implemented
applies_to: src/foundationTypes/data_model_helper.py
---

# DataModelHelper Specification

> **Status — implemented.** This spec matches the current implementation of
> `DataModelHelper`. All surfaces described below exist in code:
> `from_dict`, `to_dict`, the snake_case `save_to_file` / `load_from_file`,
> `from_env` (env-var resolution), `to_bytes` / `from_bytes`, `to_wire` / `from_wire`,
> structured logging, and the `from_*` / `to_*` helper converters. Keep this spec in
> sync with `src/foundationTypes/data_model_helper.py` when the class changes.

## Overview

`DataModelHelper` is an abstract base class that standardizes serialization,
deserialization, environment-based configuration, and protocol wire encoding for
Python data models.

It is intended to be used by:

- Quicktype-generated dataclasses
- Manually implemented dataclasses
- Configuration models
- Protocol message models

It provides a consistent interface for converting between: Python objects,
dictionaries, JSON bytes, JSON files, environment variables, and protocol wire formats.

## Design Goals

1. Provide a common serialization API across all data models.
2. Support type-safe conversion between objects and dictionaries.
3. Support JSON persistence and transport.
4. Support environment variable configuration with defaults.
5. Support pluggable protocol encoders/decoders.
6. Keep protocol-specific logic separate from model definitions.
7. Provide structured logging for all serialization operations.

## Core Requirements

All subclasses MUST implement the canonical conversion between a model instance and
its dictionary representation. Quicktype-generated subclasses implement `from_dict`
as a `@staticmethod`; the base class declares it as a `@classmethod` that raises
`NotImplementedError`:

```python
@staticmethod
def from_dict(obj: Any) -> "MyModel": ...

def to_dict(self) -> dict[str, Any]: ...
```

## Model Lifecycle

```text
Environment Variables
         │
         ▼
    from_env()
         │
         ▼
     from_dict()
         │
         ▼
   DataModelHelper
         │
 ┌───────┼────────┬────────┬─────────┐
 ▼       ▼        ▼        ▼         ▼
to_dict to_bytes to_wire save_file JSON
```

## Subclass Contract

```python
@dataclass
class UserModel(DataModelHelper):
    name: str
    age: int

    @staticmethod
    def from_dict(obj: Any) -> "UserModel":
        return UserModel(name=obj["name"], age=obj["age"])

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "age": self.age}
```

## Environment Variable Resolution

Models may define environment-backed defaults via the `_env_mapping` ClassVar,
mapping each JSON key to `(ENV_VAR_NAME, default_value, coercion_function)`:

```python
_env_mapping = {
    "host": ("API_HOST", "localhost", str),
    "port": ("API_PORT", 8080, int),
}
```

Subclasses MUST *reassign* `_env_mapping` (never mutate the inherited dict in place):
the base-class default is an empty dict shared by every subclass that does not
override it.

### Resolution order

For each configured field, resolve in this order:

1. Explicit value from the input dictionary
2. Environment variable value
3. Hardcoded default

For `_env_mapping = {"timeout": ("APP_TIMEOUT", 30, int)}`:

| Input   | Environment | Result |
| ------- | ----------- | ------ |
| 10      | 20          | 10     |
| None    | 20          | 20     |
| Missing | 20          | 20     |
| Missing | Missing     | 30     |

### `from_env()`

Constructs a model instance using explicit overrides → environment variables →
defaults:

```python
config = AppConfig.from_env()
config = AppConfig.from_env({"host": "localhost"})  # with overrides
```

## Dictionary Serialization

### `from_dict()`

```python
@staticmethod
def from_dict(obj: Any) -> DataModelHelper
```

- MUST validate input structure.
- MUST construct a fully initialized model.
- SHOULD raise an exception on invalid data.

### `to_dict()`

```python
def to_dict(self) -> dict[str, Any]
```

- MUST return JSON-serializable values.
- MUST preserve semantic data.

## JSON Byte Serialization

### `to_bytes()`

```python
def to_bytes(encoding: str = "utf-8") -> bytes
```

Serializes the model to JSON encoded as bytes (UTF-8 by default).

### `from_bytes()`

```python
@classmethod
def from_bytes(cls, data: bytes, encoding: str = "utf-8")
```

Deserializes JSON bytes into a model instance: `model = MyModel.from_bytes(payload)`.

## File Serialization

### `save_to_file()`

```python
def save_to_file(filename: Path) -> None
```

Writes the model to disk as pretty-printed JSON: UTF-8, 4-space indentation.

### `load_from_file()`

```python
@classmethod
def load_from_file(cls, filename: Path)
```

Loads a model from a JSON file.

## Wire Protocol Support

`DataModelHelper` supports protocol-specific serialization through externally
assigned encoder and decoder functions, held in the `wire_encode` / `wire_decode`
ClassVars (default `None`). The model itself contains no protocol logic.

### Encoder / decoder

Assigned at runtime (by convention in a `wire_config.py`):

```python
MyCommand.wire_encode = encode   # def encode(instance, **kwargs) -> str
MyCommand.wire_decode = decode   # def decode(cls, wire_str)
```

### `to_wire()` / `from_wire()`

```python
def to_wire(**kwargs) -> str
@classmethod
def from_wire(cls, wire_str: str)
```

```python
wire = command.to_wire()
command = Command.from_wire(wire)
```

## Logging Requirements

All public serialization methods MUST log operation start, successful completion, and
failures (with stack traces). Covered methods: `from_env`, `to_bytes`, `from_bytes`,
`save_to_file`, `load_from_file`, `to_wire`, `from_wire`. Failure logging SHALL include
`exc_info=True` to preserve traceback information. The module logger is obtained via
`getLogger(__name__)`.

## Helper Conversion Functions

The module provides helper functions for generated serializers:

| Function | Behavior |
| --- | --- |
| `from_str(x)` | Validates and returns a string. |
| `from_int(x)` | Validates and returns an integer. |
| `from_float(x)` | Accepts `float`/`int`, returns `float`. |
| `from_bool(x)` | Validates and returns a boolean. |
| `from_list(f, x)` | Applies converter `f` to every item. |
| `from_dict(f, x)` | Applies converter `f` to every value. |
| `from_union([a, b], value)` | Attempts converters in order until one succeeds. |
| `to_enum(MyEnum, value)` | Converts an enum instance to its wire value. |
| `to_class(MyModel, value)` | Converts a model instance using `to_dict()`. |
| `from_none(x)` | Validates a null value. |

## Error Handling

- **Abstract methods.** `from_dict()` and `to_dict()` MUST raise `NotImplementedError`
  in the base class.
- **Wire serialization.** `to_wire()` and `from_wire()` MUST raise
  `NotImplementedError` when no encoder/decoder has been configured.
- **JSON errors.** The implementation propagates underlying exceptions without
  wrapping: `json.JSONDecodeError`, `OSError`, `UnicodeDecodeError`, and validation
  errors raised by subclass implementations.

## Compliance Requirements

A compliant `DataModelHelper` subclass MUST:

1. Implement `from_dict()`.
2. Implement `to_dict()`.
3. Return JSON-serializable values from `to_dict()`.
4. Be constructible through `from_dict()`.
5. Preserve model state through `model → to_dict() → from_dict()` without data loss.
6. Preserve model state through `model → to_bytes() → from_bytes()` without data loss.
7. Preserve model state through `model → save_to_file() → load_from_file()` without
   data loss.
