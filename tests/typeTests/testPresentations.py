import unittest


class TestPresentationsImport(unittest.TestCase):
    """Import-time contract for the generated Presentations module (chunk 02)."""

    def test_import_presentation_deck(self) -> None:
        from foundationTypes.presentationTypes import PresentationDeck

        self.assertTrue(hasattr(PresentationDeck, "from_dict"))
        self.assertTrue(hasattr(PresentationDeck, "to_dict"))

    def test_import_all_four_top_level_classes(self) -> None:
        from foundationTypes.presentationTypes import (
            PresentationColorTheme,
            PresentationDeck,
            PresentationMetadata,
            PresentationSlideLayouts,
        )

        for cls in (
            PresentationColorTheme,
            PresentationMetadata,
            PresentationSlideLayouts,
            PresentationDeck,
        ):
            self.assertTrue(hasattr(cls, "from_dict"))
            self.assertTrue(hasattr(cls, "to_dict"))


if __name__ == "__main__":
    unittest.main()
