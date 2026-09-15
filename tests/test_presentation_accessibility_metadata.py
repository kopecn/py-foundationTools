"""Tests for accessibility and document core-property metadata fields (chunk 07).

Contract: .claude/specs/presentationSchema.md R21 (accessibility/portability) and R22
(document core-property metadata). ``image`` and ``mermaid`` blocks MAY declare
``altText``. The typography ``defaults`` object MAY declare an ordered
``fontFallbackStack`` and a ``substitutionAllowed`` flag. ``PresentationMetadata`` gains
an optional ``keywords`` field -- the only genuinely new core-property field, since
``subject``/``description``, ``author``, and ``revision``/``version`` are dual names for
the pre-existing ``description``, ``author``, and ``version`` fields respectively (the
same reuse pattern R22 already applies to ``title``). Every field here is additive,
optional, and default-less.
"""

from foundationTypes.presentationTypes.Presentations import (
    ContentBlock,
    ContentType,
    Defaults,
    File,
    PresentationMetadata,
)


def test_alttext_roundtrip() -> None:
    image_block = ContentBlock(
        region="hero",
        type=ContentType.IMAGE,
        source="hero.png",
        alt_text="Quarterly revenue trending upward across four regions.",
    )
    mermaid_block = ContentBlock(
        region="diagram",
        type=ContentType.MERMAID,
        mermaid_source="graph TD; A-->B;",
        alt_text="Flowchart showing the deployment pipeline from commit to production.",
    )

    round_tripped_image = ContentBlock.from_dict(image_block.to_dict())
    round_tripped_mermaid = ContentBlock.from_dict(mermaid_block.to_dict())

    assert round_tripped_image == image_block
    assert round_tripped_image.alt_text == image_block.alt_text
    assert round_tripped_mermaid == mermaid_block
    assert round_tripped_mermaid.alt_text == mermaid_block.alt_text


def test_font_fallback_stack_roundtrip() -> None:
    defaults = Defaults(
        font_family="Helvetica Neue",
        font_fallback_stack=["Helvetica Neue", "Arial", "Liberation Sans"],
        substitution_allowed=True,
    )

    round_tripped = Defaults.from_dict(defaults.to_dict())

    assert round_tripped == defaults
    assert round_tripped.font_fallback_stack == [
        "Helvetica Neue",
        "Arial",
        "Liberation Sans",
    ]
    assert round_tripped.substitution_allowed is True


def test_core_property_metadata_roundtrip() -> None:
    metadata = PresentationMetadata(
        author="Jane Author",
        company="Acme",
        date="2026-09-15",
        file=File(name="deck.pptx"),
        title="Quarterly Review",
        description="Board-level quarterly performance review.",
        version="2.1",
        keywords="quarterly, revenue, board",
    )

    round_tripped = PresentationMetadata.from_dict(metadata.to_dict())

    assert round_tripped == metadata
    # R22: subject/description, author, and revision/version are the pre-existing
    # fields reused directly -- only keywords is a genuinely new field.
    assert round_tripped.description == metadata.description
    assert round_tripped.author == metadata.author
    assert round_tripped.version == metadata.version
    assert round_tripped.keywords == "quarterly, revenue, board"


def test_pre_existing_metadata_still_roundtrips() -> None:
    # A deck predating altText, the font fallback stack, and keywords.
    metadata = PresentationMetadata(
        author="a",
        company="c",
        date="2026-01-01",
        file=File(name="deck.pptx"),
        title="Deck",
    )
    block = ContentBlock(region="hero", type=ContentType.IMAGE, source="hero.png")
    defaults = Defaults(font_family="Aptos")

    round_tripped_metadata = PresentationMetadata.from_dict(metadata.to_dict())
    round_tripped_block = ContentBlock.from_dict(block.to_dict())
    round_tripped_defaults = Defaults.from_dict(defaults.to_dict())

    assert round_tripped_metadata == metadata
    assert round_tripped_metadata.keywords is None
    assert round_tripped_block == block
    assert round_tripped_block.alt_text is None
    assert round_tripped_defaults == defaults
    assert round_tripped_defaults.font_fallback_stack is None
    assert round_tripped_defaults.substitution_allowed is None
