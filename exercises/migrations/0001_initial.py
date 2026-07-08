import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="nom")),
                ("slug", models.SlugField(max_length=140, unique=True, verbose_name="slug")),
                ("description", models.TextField(blank=True, verbose_name="descripcio")),
            ],
            options={
                "verbose_name": "categoria",
                "verbose_name_plural": "categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=80, unique=True, verbose_name="nom d'usuari")),
                (
                    "access_code",
                    models.CharField(
                        max_length=4,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^\\d{4}$", "El codi ha de tenir exactament 4 xifres."
                            )
                        ],
                        verbose_name="codi de 4 xifres",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "perfil d'estudiant",
                "verbose_name_plural": "perfils d'estudiant",
                "ordering": ["username"],
            },
        ),
        migrations.CreateModel(
            name="Exercise",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, max_length=180, verbose_name="titol")),
                ("statement", models.TextField(verbose_name="enunciat")),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("open_three", "3 preguntes obertes"),
                            ("multiple_choice", "Preguntes tipus test"),
                        ],
                        max_length=30,
                        verbose_name="tipus",
                    ),
                ),
                ("feedback", models.TextField(blank=True, verbose_name="comentari")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="exercises", to="exercises.category"
                    ),
                ),
            ],
            options={
                "verbose_name": "exercici",
                "verbose_name_plural": "exercicis",
                "ordering": ["category__name", "title", "id"],
            },
        ),
        migrations.CreateModel(
            name="Attempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(blank=True, max_length=40)),
                ("correct_count", models.PositiveSmallIntegerField(default=0)),
                ("total_count", models.PositiveSmallIntegerField(default=0)),
                ("score", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=5)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "exercise",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="exercises.exercise"
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="attempts",
                        to="exercises.studentprofile",
                    ),
                ),
            ],
            options={
                "verbose_name": "intent",
                "verbose_name_plural": "intents",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prompt", models.CharField(max_length=300, verbose_name="pregunta")),
                (
                    "kind",
                    models.CharField(
                        choices=[("open", "Resposta oberta"), ("multiple_choice", "Tipus test")],
                        max_length=30,
                        verbose_name="tipus de pregunta",
                    ),
                ),
                ("order", models.PositiveSmallIntegerField(default=1, verbose_name="ordre")),
                ("options", models.JSONField(blank=True, default=list, verbose_name="opcions")),
                ("correct_answers", models.JSONField(default=list, verbose_name="respostes correctes")),
                ("explanation", models.TextField(blank=True, verbose_name="comentari")),
                (
                    "exercise",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="exercises.exercise"
                    ),
                ),
            ],
            options={
                "verbose_name": "pregunta",
                "verbose_name_plural": "preguntes",
                "ordering": ["exercise_id", "order", "id"],
                "unique_together": {("exercise", "order")},
            },
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("raw_answer", models.TextField(verbose_name="resposta")),
                ("is_correct", models.BooleanField(default=False, verbose_name="correcta")),
                (
                    "attempt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="exercises.attempt"
                    ),
                ),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="exercises.question")),
            ],
            options={
                "verbose_name": "resposta",
                "verbose_name_plural": "respostes",
                "ordering": ["question__order"],
            },
        ),
    ]
