"""Tests for the pure theme/layout migration result (chunk 10).

Contract: .claude/specs/presentationSchema.md (R13),
.claude/plans/10-layout-migration.md, and fix-11. Migration never infers a
correspondence: every layout id, region id, and color reference in a scoped
dimension must appear explicitly in a ``MigrationMapping``. ``None`` leaves a
dimension out of scope; a mapping, including an empty one, brings it into
scope. An unresolved scoped reference is left unchanged on the migrated deck
and reported in ``MigrationResult.unplaced`` -- never silently dropped.
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
        mapping = MigrationMapping(
            layout_map={"one-column": "one-column"}, region_map={}
        )

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

        result = migrate_deck(deck, MigrationMapping(layout_map={}))

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
            layout_map={"one-column": "one-column"},
            region_map={"body": "body"},
            color_map={},
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

    def test_omitted_dimensions_are_out_of_scope(self) -> None:
        slide = Slide(layout="title", number=1)
        deck = _deck(slide)

        result = migrate_deck(deck, MigrationMapping())

        assert result.ok
        assert result.unplaced == ()
        assert result.deck.to_dict() == deck.to_dict()

    def test_explicit_empty_layout_mapping_reports_unresolved_layout(self) -> None:
        slide = Slide(layout="title", number=1)
        deck = _deck(slide)

        result = migrate_deck(deck, MigrationMapping(layout_map={}))

        assert not result.ok
        assert result.unplaced == (
            UnplacedContent(
                slide_number=1,
                kind="layout",
                old_reference="title",
                reason="no layout mapping entry for 'title'",
            ),
        )
        assert result.deck.to_dict() == deck.to_dict()


class TestVersionStampIntegrity:
    def _versioned_deck(self) -> PresentationDeck:
        return _deck(
            Slide(
                layout="old-layout",
                number=1,
                content=[
                    ContentBlock(
                        region="old-region",
                        type=ContentType.TEXT,
                        text="keep me",
                        style=Style(color=ThemeColorRef.TEXT),
                    )
                ],
            ),
            theme_version=ThemeVersion(id="old-theme", version="1"),
            layout_version=LayoutVersion(id="old-layouts", version="1"),
        )

    def test_color_failure_keeps_theme_stamp_but_updates_layout_stamp(self) -> None:
        deck = self._versioned_deck()
        new_theme = ThemeVersion(id="new-theme", version="2")
        new_layout = LayoutVersion(id="new-layouts", version="2")

        result = migrate_deck(
            deck,
            MigrationMapping(
                to_theme_version=new_theme,
                to_layout_version=new_layout,
                layout_map={"old-layout": "new-layout"},
                region_map={"old-region": "new-region"},
                color_map={},
            ),
        )

        assert not result.ok
        assert result.deck.metadata.theme_version == deck.metadata.theme_version
        assert result.deck.metadata.layout_version == new_layout
        assert {item.kind for item in result.unplaced} == {"color"}

    def test_layout_failure_keeps_layout_stamp_but_updates_theme_stamp(self) -> None:
        deck = self._versioned_deck()
        new_theme = ThemeVersion(id="new-theme", version="2")
        new_layout = LayoutVersion(id="new-layouts", version="2")

        result = migrate_deck(
            deck,
            MigrationMapping(
                to_theme_version=new_theme,
                to_layout_version=new_layout,
                layout_map={},
                region_map={"old-region": "new-region"},
                color_map={"text": "accentBlue.accent"},
            ),
        )

        assert not result.ok
        assert result.deck.metadata.theme_version == new_theme
        assert result.deck.metadata.layout_version == deck.metadata.layout_version
        assert {item.kind for item in result.unplaced} == {"layout"}

    def test_region_failure_keeps_layout_stamp_but_updates_theme_stamp(self) -> None:
        deck = self._versioned_deck()
        new_theme = ThemeVersion(id="new-theme", version="2")
        new_layout = LayoutVersion(id="new-layouts", version="2")

        result = migrate_deck(
            deck,
            MigrationMapping(
                to_theme_version=new_theme,
                to_layout_version=new_layout,
                layout_map={"old-layout": "new-layout"},
                region_map={},
                color_map={"text": "accentBlue.accent"},
            ),
        )

        assert not result.ok
        assert result.deck.metadata.theme_version == new_theme
        assert result.deck.metadata.layout_version == deck.metadata.layout_version
        assert {item.kind for item in result.unplaced} == {"region"}

    def test_target_versions_are_not_stamped_when_dimensions_are_out_of_scope(self) -> None:
        deck = self._versioned_deck()

        result = migrate_deck(
            deck,
            MigrationMapping(
                to_theme_version=ThemeVersion(id="new-theme", version="2"),
                to_layout_version=LayoutVersion(id="new-layouts", version="2"),
            ),
        )

        assert result.ok
        assert result.unplaced == ()
        assert result.deck.to_dict() == deck.to_dict()

    def test_layout_target_is_not_stamped_when_region_dimension_is_out_of_scope(self) -> None:
        deck = self._versioned_deck()

        result = migrate_deck(
            deck,
            MigrationMapping(
                to_layout_version=LayoutVersion(id="new-layouts", version="2"),
                layout_map={"old-layout": "new-layout"},
            ),
        )

        assert result.ok
        assert result.deck.slides[0].layout == "new-layout"
        assert result.deck.metadata.layout_version == deck.metadata.layout_version

    def test_layout_target_is_not_stamped_when_layout_dimension_is_out_of_scope(self) -> None:
        deck = self._versioned_deck()

        result = migrate_deck(
            deck,
            MigrationMapping(
                to_layout_version=LayoutVersion(id="new-layouts", version="2"),
                region_map={"old-region": "new-region"},
            ),
        )

        assert result.ok
        migrated_content = result.deck.slides[0].content
        assert migrated_content is not None
        assert migrated_content[0].region == "new-region"
        assert result.deck.metadata.layout_version == deck.metadata.layout_version
