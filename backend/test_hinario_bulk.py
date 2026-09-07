import unittest

try:
    from routes.api_study import parse_hymn_selection
except Exception as exc:  # pragma: no cover - intended to fail before implementation
    parse_hymn_selection = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


class HinarioBulkSelectionTests(unittest.TestCase):
    def test_parse_hymn_selection_supports_single_values_ranges_and_zero_padding(self):
        if IMPORT_ERROR is not None:
            self.fail(f"Import failed before implementation: {IMPORT_ERROR}")

        self.assertEqual(parse_hymn_selection('1'), {1})
        self.assertEqual(parse_hymn_selection('1, 5, 10'), {1, 5, 10})
        self.assertEqual(parse_hymn_selection('20-30'), set(range(20, 31)))
        self.assertEqual(parse_hymn_selection('001'), {1})
        self.assertEqual(parse_hymn_selection('1,5,10-15,30'), {1, 5, 10, 11, 12, 13, 14, 15, 30})

    def test_parse_hymn_selection_rejects_invalid_input(self):
        if IMPORT_ERROR is not None:
            self.fail(f"Import failed before implementation: {IMPORT_ERROR}")

        self.assertEqual(parse_hymn_selection('0'), set())
        self.assertEqual(parse_hymn_selection('500'), set())
        self.assertEqual(parse_hymn_selection('1-0'), set())


if __name__ == '__main__':
    unittest.main()
