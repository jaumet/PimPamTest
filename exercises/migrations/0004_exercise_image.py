from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exercises", "0003_pimpam_studentpimpam_seed"),
    ]

    operations = [
        migrations.AddField(
            model_name="exercise",
            name="image",
            field=models.URLField(blank=True, max_length=500, verbose_name="imatge"),
        ),
    ]
