from pathlib import Path
from typing import TypeVar, Type, Any, Dict, Optional
from dataclasses import dataclass, asdict, fields
import json


T = TypeVar("T", bound="DataModelHelper")


class DataModelHelper:
    """"""

    @staticmethod
    def from_dict(obj: Any) -> "DataModelHelper":
        """Override in subclass with strict typing"""
        raise NotImplementedError("from_dict must be implemented by subclasses")

    def to_dict(self) -> dict:
        """Override in subclass with strict typing"""
        raise NotImplementedError("to_dict must be implemented by subclasses")

    def save_to_file(self, filename: Path) -> None:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)

    @classmethod
    def load_from_file(cls: Type[T], filename: Path) -> T:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
