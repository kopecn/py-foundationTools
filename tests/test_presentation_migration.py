"""Tests for the pure theme/layout migration result (chunk 10).

Contract: .claude/specs/presentationSchema.md (R13) and
.claude/plans/10-layout-migration.md. Migration never infers a correspondence:
every layout id, region id, and color reference the caller wants rewritten
must appear explicitly in a ``MigrationMapping``. A reference the mapping
doesn't cover is left unchanged on the migrated deck and reported in
``MigrationResult.unplaced`` -- never silently dropped.
"""

from foundation_tools.presentation.migration import (
    MigrationMapping,
    UnplacedContent,
    migrate_deck,
)
from foundationTypes.presentationTypes.Presentations import (
    ContentBlock,
    ContentType,
    File,
    LayoutVersion,
    PresentationDeck,
    PresentationMetadata,
    Slide,
    Style,
    ThemeColorRef,
    ThemeVersion,
)


def _metadata(
    *,
    theme_version: ThemeVersion | None = None,
    layout_version: LayoutVersion | None = None,
) -> PresentationMetadata:
    return PresentationMetadata(
        author="a",
        company="c",
        date="2026-01-01",
        file=File(name="deck.pptx"),
        title="Deck",
        theme_version=theme_version,
        layout_version=layout_version,
    )


def _deck(
    *slides: Slide,
    theme_version: ThemeVersion | None = None,
    layout_version: LayoutVersion | None = None,
) -> PresentationDeck:
    metadata = _metadata(theme_version=theme_version, layout_version=layout_version)
    return PresentationDeck(metadata=metadata, slides=list(slides))


class TestSuccessfulRemap:
    def test_layout_region_color_and_version_stamp_all_update(self) -> None:
        old_theme = ThemeVersion(id="acme-2020", version="1.0")
        old_layout = LayoutVersion(id="standard-2020", version="1.0")
        new_theme = ThemeVersion(id="acme-2026", version="2.0")
        new_layout = LayoutVersion(id="standard-2026", version="2.0")
        slide = Slide(
            layout="old-one-column",
            number=1,
            content=[
                ContentBlock(
                    region="oldBody",
                    type=ContentType.TEXT,
                    text="hi",
                    style=Style(color=ThemeColorRef.ACCENT_BLUE_ACCENT),
                )
            ],
        )
        deck = _deck(slide, theme_version=old_theme, layout_version=old_layout)
        mapping = MigrationMapping(
            to_theme_version=new_theme,
            to_layout_version=new_layout,
            layout_map={"old-one-column": "new-one-column"},
            region_map={"oldBody": "newBody"},
            color_map={"accentBlue.accent": "accentTeal.accent"},
        )

        result = migrate_deck(deck, mapping)

        assert result.ok
        assert result.unplaced == ()
        assert result.deck.metadata.theme_version == new_theme
        assert result.deck.metadata.layout_version == new_layout
        migrated_slide = result.deck.slides[0]
        assert migrated_slide.layout == "new-one-column"
        assert migrated_slide.content is not None
        migrated_block = migrated_slide.content[0]
        assert migrated_block.region == "newBody"
        assert migrated_block.style is not None
        assert migrated_block.style.color == ThemeColorRef.ACCENT_TEAL_ACCENT
        # Unmapped content is untouched.
        assert migrated_block.text == "hi"


class TestUnplaceableContentIsReported:
    def test_region_with_no_mapping_entry_is_reported_and_kept(self) -> None:
        slide = Slide(
            layout="one-column",
            number=3,
            content=[ContentBlock(region="orphanRegion", type=ContentType.TEXT, text="keep me")],
        )
        deck = _deck(slide)
        mapping = MigrationMapping(layout_map={"one-column": "one-column"})

        result = migrate_deck(deck, mapping)

        migrated_content = result.deck.slides[0].content
        assert not result.ok
        assert migrated_content is not None
        assert migrated_content[0].region == "orphanRegion"
        assert migrated_content[0].text == "keep me"
        assert result.unplaced == (
            UnplacedContent(
                slide_number=3,
                kind="region",
                old_reference="orphanRegion",
                reason="no region mapping entry for 'orphanRegion'",
            ),
        )

    def test_layout_with_no_mapping_entry_is_reported_and_kept(self) -> None:
        slide = Slide(layout="mystery-layout", number=1)
        deck = _deck(slide)

        result = migrate_deck(deck, MigrationMapping())

        assert not result.ok
        assert result.deck.slides[0].layout == "mystery-layout"
        assert result.unplaced == (
            UnplacedContent(
                slide_number=1,
                kind="layout",
                old_reference="mystery-layout",
                reason="no layout mapping entry for 'mystery-layout'",
            ),
        )

    def test_color_with_no_mapping_entry_is_reported_and_kept(self) -> None:
        slide = Slide(
            layout="one-column",
            number=2,
            content=[
                ContentBlock(
                    region="body",
                    type=ContentType.TEXT,
                    text="hi",
                    style=Style(color=ThemeColorRef.TEXT),
                )
            ],
        )
        deck = _deck(slide)
        mapping = MigrationMapping(
            layout_map={"one-column": "one-column"}, region_map={"body": "body"}
        )

        result = migrate_deck(deck, mapping)

        migrated_content = result.deck.slides[0].content
        assert not result.ok
        assert migrated_content is not None
        assert migrated_content[0].style is not None
        assert migrated_content[0].style.color == ThemeColorRef.TEXT
        assert result.unplaced == (
            UnplacedContent(
                slide_number=2,
                kind="color",
                old_reference="text",
                reason="no color mapping entry for 'text'",
            ),
        )


class TestIdentityMapping:
    def test_mapping_every_reference_to_itself_is_a_no_op(self) -> None:
        slide = Slide(
            layout="one-column",
            number=1,
            content=[
                ContentBlock(
                    region="body",
                    type=ContentType.TEXT,
                    text="hi",
                    style=Style(color=ThemeColorRef.TEXT),
                )
            ],
        )
        deck = _deck(slide)
        mapping = MigrationMapping(
            layout_map={"one-column": "one-column"},
            region_map={"body": "body"},
            color_map={"text": "text"},
        )

        result = migrate_deck(deck, mapping)

        assert result.ok
        assert result.unplaced == ()
        assert result.deck.to_dict() == deck.to_dict()

    def test_empty_mapping_on_a_deck_with_no_references_is_a_no_op(self) -> None:
        slide = Slide(layout="title", number=1)
        deck = _deck(slide)

        result = migrate_deck(deck, MigrationMapping())

        assert not result.ok  # the slide's own layout id is still unmapped
        assert result.deck.to_dict() == deck.to_dict()
