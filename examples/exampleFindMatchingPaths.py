"""Usage examples for find_matching_paths. root must be an absolute directory."""

from pathlib import Path

from foundation_tools.file_tools.path_tools import find_matching_paths

# An absolute root to resolve patterns against, built relative to the home dir.
root = Path.home() / "workspace" / "data"

print("---- Downloads ----")
downloads_folder = Path.home().joinpath("Downloads")
if downloads_folder.exists() and downloads_folder.is_dir():
    files = find_matching_paths(
        starting_dir=downloads_folder,
    )
    for file in files:
        print(file)


print("\n\n\n---- Documents, pdfs ----")
downloads_folder = Path.home().joinpath("Documents")
if downloads_folder.exists() and downloads_folder.is_dir():
    files = find_matching_paths(
        starting_dir=downloads_folder,
        extensions=[".pdf"],
    )
    for file in files:
        print(file)

print("\n\n\n---- User Home, *Img* ----")
downloads_folder = Path.home()
if downloads_folder.exists() and downloads_folder.is_dir():
    files = find_matching_paths(
        starting_dir=downloads_folder,
        pattern="*code*",
    )
    for file in files:
        print(file)

# # extensions=None matches any extension.
# print(find_matching_paths(root, "config", extensions=None))

# # A relative subdirectory in the pattern, resolved beneath root.
# print(find_matching_paths(root, "invoices/*", extensions=["pdf"]))
