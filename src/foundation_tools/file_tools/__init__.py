"""
File Tools — filesystem and path helpers.

Re-exports the public surface so callers import from the package rather than the
module file: ``from foundation_tools.file_tools import find_matching_paths``.
"""

from foundation_tools.file_tools.path_tools import find_matching_paths

__all__ = ["find_matching_paths"]
