from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exercises", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="exercise",
            name="level",
            field=models.PositiveSmallIntegerField(default=1, verbose_name="nivell"),
        ),
        migrations.AlterModelOptions(
            name="exercise",
            options={
                "ordering": ["category__name", "level", "title", "id"],
                "verbose_name": "exercici",
                "verbose_name_plural": "exercicis",
            },
        ),
    ]
