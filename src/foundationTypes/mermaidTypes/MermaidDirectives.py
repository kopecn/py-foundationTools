# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_dict,
    to_class,
)
from typing import Dict, Any, TypeVar, Callable, Type, cast

T = TypeVar("T")


@dataclass
class MermaidDirectives(DataModelHelper):
    """Mermaid pre-render directives (the `%%{ ... }%%` block). API docs:
    https://mermaid.ai/open-source/config/directives.html . Placeholder: a single generic
    `init` object for now, to be refined later.
    """

    init: Dict[str, Any]
    """The `%%{init: ...}%%` directive payload. Generic object for now; to be refined later."""

    @classmethod
    def from_dict(cls, obj: Any) -> "MermaidDirectives":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        init = from_dict(lambda x: x, obj.get("init"))
        return MermaidDirectives(init)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["init"] = from_dict(lambda x: x, self.init)
        return result


def mermaid_directives_from_dict(s: Any) -> MermaidDirectives:
    return MermaidDirectives.from_dict(s)


def mermaid_directives_to_dict(x: MermaidDirectives) -> Any:
    return to_class(MermaidDirectives, x)
