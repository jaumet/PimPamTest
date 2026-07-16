from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exercises", "0004_exercise_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exercise",
            name="level",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Nivell 0 · PRI 2n-3r"),
                    (1, "Nivell 1 · PRI 3r-4t"),
                    (2, "Nivell 2 · PRI 4t-5è"),
                    (3, "Nivell 3 · PRI 5è-6è"),
                ],
                default=1,
                verbose_name="nivell",
            ),
        ),
    ]
