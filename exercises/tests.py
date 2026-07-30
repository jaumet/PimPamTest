from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Category, Exercise, normalize_answer


class NormalizeAnswerTests(SimpleTestCase):
    def test_ignores_spaces_around_currency_symbol(self):
        self.assertEqual(normalize_answer("1€"), normalize_answer("1 €"))
        self.assertEqual(normalize_answer("1€"), normalize_answer("1 €."))

    def test_ignores_case_accents_and_apostrophe_style(self):
        self.assertEqual(normalize_answer("L'ÀVIA"), normalize_answer("l’àvia"))

    def test_normalizes_decimal_separators_and_trailing_zeroes(self):
        self.assertEqual(normalize_answer("3,50 €"), normalize_answer("3.5€"))


class AnonymousHomeTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Matemàtiques", slug="matematiques")
        self.exercise = Exercise.objects.create(
            title="Sumes senzilles",
            statement="Calcula el resultat.",
            category=category,
            level=0,
            kind=Exercise.ExerciseKind.MULTIPLE_CHOICE,
        )

    def test_home_invites_practice_without_registration(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Comença a practicar")
        self.assertContains(response, "Pots començar sense registre")
        self.assertContains(response, self.exercise.get_absolute_url())

    def test_home_presents_identification_as_progress_saving_option(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "desa el teu progrés")
        self.assertContains(response, "La identificació només serveix per recordar el progrés")
