"""
Theme/layout migration: update an older deck's layout, region, and color
references to a newer corporate standard (chunk 10; see R13 and
``.claude/plans/10-layout-migration.md``).

Pure, stdlib-only, no I/O. Every correspondence this module applies -- which
old layout id, region id, or color reference maps to what new one, and which
new theme/layout identity to stamp onto the deck -- comes from an explicit
``MigrationMapping`` the caller supplies. This module infers nothing and does
not resolve, store, or discover identifiers against an actual
``PresentationSlideLayouts``/``PresentationColorTheme`` document; verifying
that a mapping is the right one for a given deck's current stamp is a
consumer decision (that verification is registry/discovery machinery, out of
scope per R13).

Each mapping dimension is explicitly scoped: ``None`` excludes that dimension,
while a mapping (including an empty one) attempts to migrate it. A scoped
reference the mapping does not cover cannot be placed on the new standard. It
is left unchanged on the migrated deck and recorded in
``MigrationResult.unplaced`` -- reported, never silently dropped. Target
versions are stamped only after all of their scoped dimensions succeed. File
writing, interactive conflict resolution, inferred remapping, and PowerPoint
rendering remain consumer responsibilities.
"""

from collections.abc import Mapping
from dataclasses import dataclass, replace

from foundation_tools.presentation.layout_resolver import RESERVED_REGION_IDS
from foundationTypes.presentationTypes.Presentations import (
    ContentBlock,
    LayoutVersion,
    PresentationDeck,
    PresentationMetadata,
    Slide,
    Style,
    ThemeColorRef,
    ThemeVersion,
)

__all__ = [
    "MigrationMapping",
    "MigrationResult",
    "UnplacedContent",
    "migrate_deck",
]


@dataclass(frozen=True)
class MigrationMapping:
    """
    Explicit old -> new correspondence for a theme/layout migration.

    Every field is supplied by the caller from a real version change; nothing
    here is inferred or looked up against an actual theme/layout document.
    """

    to_theme_version: ThemeVersion | None = None
    """New theme identity to stamp onto the migrated deck's metadata. ``None``
    leaves the deck's current ``theme_version`` stamp as-is.
    """

    to_layout_version: LayoutVersion | None = None
    """New layout identity to stamp onto the migrated deck's metadata.
    ``None`` leaves the current ``layout_version`` stamp as-is.
    """

    layout_map: Mapping[str, str] | None = None
    """Old ``Slide.layout`` id -> new layout id. ``None`` leaves layouts
    outside this migration's scope; an empty mapping explicitly scopes layouts
    but cannot resolve any layout reference.
    """

    region_map: Mapping[str, str] | None = None
    """Old ``ContentBlock.region`` id -> new region id. Reserved region ids
    (``title``, ``subtitle``, R11) are a fixed contract, not an authored
    reference, so they are never looked up here. ``None`` leaves authored
    regions outside this migration's scope; an empty mapping explicitly scopes
    them but cannot resolve any authored region reference.
    """

    color_map: Mapping[str, str] | None = None
    """Old ``ThemeColorRef`` value -> new ``ThemeColorRef`` value. ``None``
    leaves colors outside this migration's scope; an empty mapping explicitly
    scopes colors but cannot resolve any color reference.
    """


@dataclass(frozen=True)
class UnplacedContent:
    """
    One reference the mapping could not place onto the new standard.

    The referencing slide/content is left unchanged on the migrated deck;
    this record is the only trace that it still needs attention.
    """

    slide_number: int
    kind: str
    """``"layout"``, ``"region"``, or ``"color"``."""

    old_reference: str
    reason: str


@dataclass(frozen=True)
class MigrationResult:
    """Result of migrating a deck's theme/layout references (chunk 10)."""

    deck: PresentationDeck
    unplaced: tuple[UnplacedContent, ...]

    @property
    def ok(self) -> bool:
        return not self.unplaced


def _migrate_style(
    style: Style | None,
    color_map: Mapping[str, str] | None,
    slide_number: int,
    unplaced: list[UnplacedContent],
) -> Style | None:
    if color_map is None or style is None or style.color is None:
        return style
    old_ref = style.color.value
    new_ref = color_map.get(old_ref)
    if new_ref is None:
        unplaced.append(
            UnplacedContent(
                slide_number=slide_number,
                kind="color",
                old_reference=old_ref,
                reason=f"no color mapping entry for '{old_ref}'",
            )
        )
        return style
    try:
        new_color = ThemeColorRef(new_ref)
    except ValueError:
        unplaced.append(
            UnplacedContent(
                slide_number=slide_number,
                kind="color",
                old_reference=old_ref,
                reason=f"mapping target '{new_ref}' is not a known color reference",
            )
        )
        return style
    return replace(style, color=new_color)


def _migrate_block(
    block: ContentBlock,
    mapping: MigrationMapping,
    slide_number: int,
    unplaced: list[UnplacedContent],
) -> ContentBlock:
    new_region = block.region
    if mapping.region_map is not None and block.region not in RESERVED_REGION_IDS.values():
        target = mapping.region_map.get(block.region)
        if target is None:
            unplaced.append(
                UnplacedContent(
                    slide_number=slide_number,
                    kind="region",
                    old_reference=block.region,
                    reason=f"no region mapping entry for '{block.region}'",
                )
            )
        else:
            new_region = target

    new_style = _migrate_style(block.style, mapping.color_map, slide_number, unplaced)

    if new_region == block.region and new_style is block.style:
        return block
    return replace(block, region=new_region, style=new_style)


def _migrate_slide(
    slide: Slide, mapping: MigrationMapping, unplaced: list[UnplacedContent]
) -> Slide:
    new_layout = slide.layout
    if mapping.layout_map is not None:
        target = mapping.layout_map.get(slide.layout)
        if target is None:
            unplaced.append(
                UnplacedContent(
                    slide_number=slide.number,
                    kind="layout",
                    old_reference=slide.layout,
                    reason=f"no layout mapping entry for '{slide.layout}'",
                )
            )
        else:
            new_layout = target

    new_content = slide.content
    if slide.content is not None:
        new_content = [
            _migrate_block(block, mapping, slide.number, unplaced) for block in slide.content
        ]

    if new_layout == slide.layout and new_content == slide.content:
        return slide
    return replace(slide, layout=new_layout, content=new_content)


def _migrate_metadata(
    metadata: PresentationMetadata,
    mapping: MigrationMapping,
    unplaced: list[UnplacedContent],
) -> PresentationMetadata:
    failed_kinds = {item.kind for item in unplaced}
    theme_succeeded = mapping.color_map is not None and "color" not in failed_kinds
    layout_succeeded = (
        mapping.layout_map is not None
        and mapping.region_map is not None
        and failed_kinds.isdisjoint({"layout", "region"})
    )

    theme_version = metadata.theme_version
    if mapping.to_theme_version is not None and theme_succeeded:
        theme_version = mapping.to_theme_version

    layout_version = metadata.layout_version
    if mapping.to_layout_version is not None and layout_succeeded:
        layout_version = mapping.to_layout_version

    if theme_version is metadata.theme_version and layout_version is metadata.layout_version:
        return metadata
    return replace(metadata, theme_version=theme_version, layout_version=layout_version)


def migrate_deck(deck: PresentationDeck, mapping: MigrationMapping) -> MigrationResult:
    """
    Migrate a deck's layout, region, and color references per an explicit
    ``MigrationMapping``, and stamp its theme/layout identity if the mapping
    names a new one.

    Every layout id, region id, and color reference in a scoped dimension is
    looked up in its mapping. A hit is rewritten in the returned deck. A miss
    is left unchanged and recorded in ``MigrationResult.unplaced`` -- content
    this migration could not place is reported, never dropped. Theme identity
    is stamped only after scoped color migration succeeds; layout identity is
    stamped only after both layout and region migration are scoped and succeed.
    """
    unplaced: list[UnplacedContent] = []
    new_slides = [_migrate_slide(slide, mapping, unplaced) for slide in deck.slides]
    new_metadata = _migrate_metadata(deck.metadata, mapping, unplaced)

    if new_metadata is deck.metadata and new_slides == deck.slides:
        new_deck = deck
    else:
        new_deck = replace(deck, metadata=new_metadata, slides=new_slides)

    return MigrationResult(deck=new_deck, unplaced=tuple(unplaced))
