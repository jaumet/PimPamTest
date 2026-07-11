from decimal import Decimal
import re
import unicodedata

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse


def normalize_answer(value):
    value = unicodedata.normalize("NFKD", str(value).strip().casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.replace("’", "'")
    value = re.sub(r"(\d)\s*euros?\b", r"\1€", value)
    value = re.sub(r"\d+[,.]\d+", _normalize_decimal_number, value)
    value = value.strip(" \t\r\n.,;:!?")
    return re.sub(r"\s+", "", value)


def _normalize_decimal_number(match):
    whole, decimal = re.split(r"[,.]", match.group(0), maxsplit=1)
    decimal = decimal.rstrip("0")
    return whole if not decimal else f"{whole}.{decimal}"


class StudentProfile(models.Model):
    username = models.CharField("nom d'usuari", max_length=80, unique=True)
    access_code = models.CharField(
        "codi de 4 xifres",
        max_length=4,
        validators=[RegexValidator(r"^\d{4}$", "El codi ha de tenir exactament 4 xifres.")],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["username"]
        verbose_name = "perfil d'estudiant"
        verbose_name_plural = "perfils d'estudiant"

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField("nom", max_length=120, unique=True)
    slug = models.SlugField("slug", max_length=140, unique=True)
    description = models.TextField("descripcio", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Exercise(models.Model):
    class ExerciseKind(models.TextChoices):
        OPEN_THREE = "open_three", "3 preguntes obertes"
        MULTIPLE_CHOICE = "multiple_choice", "Preguntes tipus test"

    title = models.CharField("titol", max_length=180, blank=True)
    statement = models.TextField("enunciat")
    image = models.URLField("imatge", max_length=500, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="exercises")
    level = models.PositiveSmallIntegerField("nivell", default=1)
    kind = models.CharField("tipus", max_length=30, choices=ExerciseKind.choices)
    feedback = models.TextField("comentari", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category__name", "level", "title", "id"]
        verbose_name = "exercici"
        verbose_name_plural = "exercicis"

    def __str__(self):
        return self.title or f"Exercici {self.pk}"

    def get_absolute_url(self):
        return reverse("exercise_detail", kwargs={"pk": self.pk})


class Question(models.Model):
    class QuestionKind(models.TextChoices):
        OPEN = "open", "Resposta oberta"
        MULTIPLE_CHOICE = "multiple_choice", "Tipus test"

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="questions")
    prompt = models.CharField("pregunta", max_length=300)
    kind = models.CharField("tipus de pregunta", max_length=30, choices=QuestionKind.choices)
    order = models.PositiveSmallIntegerField("ordre", default=1)
    options = models.JSONField("opcions", default=list, blank=True)
    correct_answers = models.JSONField("respostes correctes", default=list)
    explanation = models.TextField("comentari", blank=True)

    class Meta:
        ordering = ["exercise_id", "order", "id"]
        unique_together = [("exercise", "order")]
        verbose_name = "pregunta"
        verbose_name_plural = "preguntes"

    def __str__(self):
        return f"{self.exercise}: {self.prompt}"

    def clean(self):
        if not isinstance(self.correct_answers, list) or not self.correct_answers:
            raise ValidationError({"correct_answers": "Cal indicar com a minim una resposta correcta."})
        if self.kind == self.QuestionKind.MULTIPLE_CHOICE:
            if not isinstance(self.options, list) or len(self.options) < 2:
                raise ValidationError({"options": "Les preguntes tipus test necessiten com a minim dues opcions."})
            invalid = set(map(str, self.correct_answers)) - set(map(str, self.options))
            if invalid:
                raise ValidationError({"correct_answers": "Les respostes correctes han d'existir dins les opcions."})

    def is_correct(self, answer):
        if self.kind == self.QuestionKind.OPEN:
            normalized = normalize_answer(answer)
            return normalized in {normalize_answer(value) for value in self.correct_answers}
        return str(answer) in {str(value) for value in self.correct_answers}


class Attempt(models.Model):
    student = models.ForeignKey(StudentProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="attempts")
    session_key = models.CharField(max_length=40, blank=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="attempts")
    correct_count = models.PositiveSmallIntegerField(default=0)
    total_count = models.PositiveSmallIntegerField(default=0)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "intent"
        verbose_name_plural = "intents"

    def __str__(self):
        return f"{self.exercise} - {self.score}%"


class PimPam(models.Model):
    class Rarity(models.IntegerChoices):
        ONE = 1, "1 estrella"
        TWO = 2, "2 estrelles"
        THREE = 3, "3 estrelles"
        FOUR = 4, "4 estrelles"
        FIVE = 5, "5 estrelles"

    name = models.CharField("nom", max_length=80, unique=True)
    animal = models.CharField("animal", max_length=80)
    rarity = models.PositiveSmallIntegerField("valor", choices=Rarity.choices)
    description = models.CharField("descripcio", max_length=180)

    class Meta:
        ordering = ["rarity", "name"]
        verbose_name = "PimPam"
        verbose_name_plural = "PimPams"

    def __str__(self):
        return self.name

    @property
    def star_label(self):
        return "*" * self.rarity

    @property
    def visual_class(self):
        seed = sum(ord(char) for char in self.name)
        return " ".join(
            [
                f"shape-{seed % 10}",
                f"ears-{seed % 8}",
                f"feature-{seed % 10}",
                f"pattern-{seed % 9}",
                f"mood-{seed % 5}",
                f"motion-{seed % 6}",
            ]
        )

    @property
    def visual_style(self):
        seed = sum((index + 1) * ord(char) for index, char in enumerate(self.name + self.animal))
        hue = seed % 360
        secondary = (hue + 82 + self.rarity * 17) % 360
        accent = (hue + 185 + self.rarity * 11) % 360
        return (
            f"--pimpam-color:hsl({hue} 92% 58%);"
            f"--pimpam-secondary:hsl({secondary} 94% 55%);"
            f"--pimpam-accent:hsl({accent} 98% 62%);"
        )

    @property
    def initial(self):
        return self.name[:1].upper()


class StudentPimPam(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="pimpams")
    pimpam = models.ForeignKey(PimPam, on_delete=models.CASCADE, related_name="awards")
    attempt = models.OneToOneField(Attempt, null=True, blank=True, on_delete=models.SET_NULL, related_name="pimpam_award")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-awarded_at"]
        verbose_name = "PimPam guanyat"
        verbose_name_plural = "PimPams guanyats"

    def __str__(self):
        return f"{self.student} - {self.pimpam}"


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    raw_answer = models.TextField("resposta")
    is_correct = models.BooleanField("correcta", default=False)

    class Meta:
        ordering = ["question__order"]
        verbose_name = "resposta"
        verbose_name_plural = "respostes"
