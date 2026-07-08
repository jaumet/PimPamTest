# PimPamTest

Aplicacio Django per crear, importar i resoldre exercicis tipus test o de resposta oberta per a primaria i secundaria.

## Desenvolupament local

1. Crea un entorn virtual i instal-la dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Arrenca PostgreSQL:

```bash
docker compose up -d db
```

3. Configura l'entorn:

```bash
cp .env.example .env
```

Si no crees `.env`, Django fara servir SQLite local per facilitar proves rapides.

4. Crea la base de dades i un administrador:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Arrenca el servidor:

```bash
python manage.py runserver
```

## Funcionalitat inicial

- Exercicis organitzats per categoria.
- Preguntes obertes amb diverses respostes correctes possibles.
- Preguntes tipus test amb opcions i resposta correcta.
- Acces opcional d'estudiant amb nom d'usuari i codi de 4 xifres.
- Resolucio anonima amb resultats per sessio.
- Creacio d'exercicis via formulari.
- Importacio d'exercicis des d'un JSON.

El format JSON esta documentat a `docs/exercise-json-format.md`.
Hi ha un exemple importable a `examples/exercises.sample.json`.
