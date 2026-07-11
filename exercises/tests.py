from django.test import SimpleTestCase

from .models import normalize_answer


class NormalizeAnswerTests(SimpleTestCase):
    def test_ignores_spaces_around_currency_symbol(self):
        self.assertEqual(normalize_answer("1€"), normalize_answer("1 €"))
        self.assertEqual(normalize_answer("1€"), normalize_answer("1 €."))

    def test_ignores_case_accents_and_apostrophe_style(self):
        self.assertEqual(normalize_answer("L'ÀVIA"), normalize_answer("l’àvia"))

    def test_normalizes_decimal_separators_and_trailing_zeroes(self):
        self.assertEqual(normalize_answer("3,50 €"), normalize_answer("3.5€"))
