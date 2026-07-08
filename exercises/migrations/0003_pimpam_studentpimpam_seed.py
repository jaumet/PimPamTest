import django.db.models.deletion
from django.db import migrations, models


PIMPAMS = [
    ("Brinco", "conill", 1, "Salta quan veu una resposta bona."),
    ("Mofli", "erico", 1, "Petit i valent, sempre busca pistes."),
    ("Tona", "tortuga", 1, "Avanca a poc a poc i no es rendeix."),
    ("Nuriu", "esquirol", 1, "Guarda idees brillants per despres."),
    ("Piulet", "ocell", 1, "Canta quan aprens una paraula nova."),
    ("Ralet", "ratoli", 1, "Troba camins curts per pensar millor."),
    ("Bamba", "granota", 1, "Fa salts petits fins arribar lluny."),
    ("Cuca", "marieta", 1, "Porta sort als primers intents."),
    ("Llumet", "cuca de llum", 1, "Encen idees quan costa una pregunta."),
    ("Trufa", "porquet", 1, "Busca tresors amagats als textos."),
    ("Zarpin", "gat", 2, "Camina en silenci i observa molt be."),
    ("Volti", "ratpenat", 2, "S'orienta fins i tot en preguntes fosques."),
    ("Potaqua", "lludriga", 2, "Juga amb les respostes fins trobar la bona."),
    ("Becson", "anec", 2, "Sap moure's per terra i per aigua."),
    ("Mistral", "guineu", 2, "Te idees rapides i elegants."),
    ("Nivol", "cabra", 2, "Puja nivells sense por."),
    ("Rinxol", "ovella", 2, "Suau, tranquil i molt constant."),
    ("Patxoc", "gos", 2, "No abandona mai un exercici."),
    ("Closca", "cranc", 2, "Protegeix les respostes importants."),
    ("Suri", "sargantana", 2, "Canvia d'estrategia molt rapid."),
    ("Drim", "dofi", 3, "Enten patrons i juga amb les ones."),
    ("Flamar", "flamenc", 3, "Mant l'equilibri fins al final."),
    ("Rocpan", "os", 3, "Fort, pacient i bon lector."),
    ("Lirax", "linx", 3, "Veu detalls que molts no veuen."),
    ("Kiri", "koala", 3, "Tranquil per fora, savi per dins."),
    ("Mantisca", "mantis", 3, "Espera el moment exacte per respondre."),
    ("Orbi", "mussol", 3, "Apren millor quan tot esta en calma."),
    ("Quira", "cavall", 3, "Corre amb energia cap al repte."),
    ("Nubir", "camaleo", 3, "S'adapta a cada tipus de pregunta."),
    ("Bruc", "castor", 3, "Construeix solucions pas a pas."),
    ("Aural", "aguila", 4, "Mira l'exercici des de molt amunt."),
    ("Glacialp", "llop", 4, "Fred de cap i valent de cor."),
    ("Coralun", "cavallet de mar", 4, "Petit, magic i molt dificil de trobar."),
    ("Magnir", "elefant", 4, "Recorda tot el que has apres."),
    ("Selen", "cigne", 4, "Elegant quan la resposta es precisa."),
    ("Bromax", "biso", 4, "Empeny els reptes mes grans."),
    ("Vespir", "vespa", 4, "Rapida, fina i concentrada."),
    ("Dauric", "lleo", 4, "Premi de coratge i atencio."),
    ("Velox", "guepard", 4, "Arriba rapid quan domines el tema."),
    ("Marfil", "rinoceront", 4, "No s'atura davant preguntes dificils."),
    ("Astros", "falco", 5, "Un PimPam llegendari de mirada clara."),
    ("Bravon", "pantera", 5, "Apareix quan jugues amb molta forca."),
    ("Cobal", "orca", 5, "Neda per reptes enormes sense perdre el ritme."),
    ("Dorak", "tigre blanc", 5, "Rar, brillant i molt poderos."),
    ("Eclip", "cobra", 5, "Concentracio absoluta abans de respondre."),
    ("Ferox", "goril-la", 5, "Energia gegant per superar nivells."),
    ("Galion", "balena", 5, "Porta memoria profunda i calma."),
    ("Helix", "jaguar", 5, "Es mou amb precisio entre opcions."),
    ("Ignar", "fennec", 5, "Orelles grans per escoltar pistes."),
    ("Jambo", "pao", 5, "Obre colors quan fas una gran partida."),
]


def seed_pimpams(apps, schema_editor):
    PimPam = apps.get_model("exercises", "PimPam")
    for name, animal, rarity, description in PIMPAMS:
        PimPam.objects.get_or_create(
            name=name,
            defaults={"animal": animal, "rarity": rarity, "description": description},
        )


def unseed_pimpams(apps, schema_editor):
    PimPam = apps.get_model("exercises", "PimPam")
    PimPam.objects.filter(name__in=[name for name, _animal, _rarity, _description in PIMPAMS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("exercises", "0002_exercise_level"),
    ]

    operations = [
        migrations.CreateModel(
            name="PimPam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True, verbose_name="nom")),
                ("animal", models.CharField(max_length=80, verbose_name="animal")),
                (
                    "rarity",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "1 estrella"),
                            (2, "2 estrelles"),
                            (3, "3 estrelles"),
                            (4, "4 estrelles"),
                            (5, "5 estrelles"),
                        ],
                        verbose_name="valor",
                    ),
                ),
                ("description", models.CharField(max_length=180, verbose_name="descripcio")),
            ],
            options={
                "verbose_name": "PimPam",
                "verbose_name_plural": "PimPams",
                "ordering": ["rarity", "name"],
            },
        ),
        migrations.CreateModel(
            name="StudentPimPam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("awarded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "attempt",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pimpam_award",
                        to="exercises.attempt",
                    ),
                ),
                (
                    "pimpam",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="awards", to="exercises.pimpam"
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pimpams",
                        to="exercises.studentprofile",
                    ),
                ),
            ],
            options={
                "verbose_name": "PimPam guanyat",
                "verbose_name_plural": "PimPams guanyats",
                "ordering": ["-awarded_at"],
            },
        ),
        migrations.RunPython(seed_pimpams, unseed_pimpams),
    ]
