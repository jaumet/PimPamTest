from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Attempt, Category, Exercise, PimPam, Question, StudentPimPam, StudentProfile, normalize_answer


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


class LoggedInHomeTests(TestCase):
    def setUp(self):
        self.student = StudentProfile.objects.create(username="Jana", access_code="1234")
        category = Category.objects.create(name="Medi", slug="medi")
        self.exercise = Exercise.objects.create(
            title="Ecosistemes",
            statement="Tria la resposta correcta.",
            category=category,
            level=1,
            kind=Exercise.ExerciseKind.MULTIPLE_CHOICE,
        )
        Question.objects.create(
            exercise=self.exercise,
            prompt="Que es un ecosistema?",
            kind=Question.QuestionKind.OPEN,
            order=1,
            correct_answers=["Un conjunt d'essers vius i el medi."],
        )
        self.attempt = Attempt.objects.create(
            student=self.student,
            exercise=self.exercise,
            total_count=1,
            correct_count=1,
            score=100,
        )
        pimpam = PimPam.objects.create(name="Brillu", animal="gat", rarity=3, description="Premi brillant")
        StudentPimPam.objects.create(student=self.student, pimpam=pimpam, attempt=self.attempt)
        session = self.client.session
        session["student_id"] = self.student.pk
        session.save()

    def test_logged_home_uses_questions_and_history_tabs(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Preguntes")
        self.assertContains(response, "Historial")
        self.assertNotContains(response, "Exercicis per fer")

    def test_history_tab_lists_attempts(self):
        response = self.client.get(f"{reverse('home')}?tab=exercises")

        self.assertContains(response, "Categoria")
        self.assertContains(response, "Nivell")
        self.assertContains(response, "Pregunta")
        self.assertContains(response, "Vegades feta")
        self.assertContains(response, "Ecosistemes")
        self.assertContains(response, "Brillu")

    def test_result_page_does_not_repeat_pimpam_award_block_or_link(self):
        response = self.client.get(reverse("attempt_result", kwargs={"pk": self.attempt.pk}))

        self.assertNotContains(response, "Veure els teus PimPams")
        self.assertNotContains(response, "Has guanyat un PimPam!")
