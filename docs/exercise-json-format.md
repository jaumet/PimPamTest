# Format JSON d'exercicis

El fitxer d'importacio ha de ser una array d'exercicis.

## Regla important sobre enunciat i instruccions

- `statement` es el text general de l'exercici.
- `questions[].prompt` es l'enunciat concret de cada pregunta.
- Si un exercici te una sola pregunta, la web destaca `questions[0].prompt` dins el requadre principal, i `statement` queda com a instruccio secundaria.
- Si un exercici te diverses preguntes, la web destaca `statement` dins el requadre principal, i cada `prompt` apareix a cada pregunta.

Per tant:

- Per comprensio lectora o problemes amb text llarg: posa el text important a `statement`.
- Per exercicis d'una sola pregunta tipus test: posa la instruccio a `statement` i la pregunta real a `prompt`.

## Exemple amb text llarg i diverses preguntes

```json
[
  {
    "title": "Comprensio lectora 1",
    "statement": "La Laia va anar al parc amb el seu germa. Van jugar a pilota fins que va començar a ploure.",
    "level": 1,
    "kind": "open_three",
    "feedback": "Revisa el text si has fallat alguna resposta.",
    "category": {
      "name": "Comprensio lectora",
      "slug": "comprensio-lectora",
      "description": "Textos curts amb preguntes de comprensio."
    },
    "questions": [
      {
        "prompt": "Com es diu la protagonista?",
        "kind": "open",
        "order": 1,
        "correct_answers": ["Laia", "la Laia"],
        "explanation": "El nom apareix a la primera frase."
      },
      {
        "prompt": "On passa la historia?",
        "kind": "multiple_choice",
        "order": 2,
        "options": ["A l'escola", "Al parc", "A casa"],
        "correct_answers": ["Al parc"],
        "explanation": "El text diu que son al parc."
      }
    ]
  }
]
```

## Exemple d'una sola pregunta tipus test

```json
[
  {
    "title": "Els ecosistemes",
    "statement": "Tria la resposta correcta sobre els ecosistemes.",
    "level": 1,
    "kind": "multiple_choice",
    "category": {
      "name": "Medi",
      "slug": "medi"
    },
    "questions": [
      {
        "prompt": "Que es un ecosistema?",
        "kind": "multiple_choice",
        "order": 1,
        "options": [
          "Un conjunt d'essers vius i el medi on viuen.",
          "Una maquina per moure objectes.",
          "Una roca molt dura.",
          "Una eina per mesurar el temps."
        ],
        "correct_answers": ["Un conjunt d'essers vius i el medi on viuen."],
        "explanation": "Un ecosistema inclou els essers vius i el lloc on viuen."
      }
    ]
  }
]
```

Valors admesos:

- `kind` d'exercici: `open_three` o `multiple_choice`.
- `level`: nivell numeric de l'exercici. Si no s'indica, es desa com a `1`.
- `kind` de pregunta: `open` o `multiple_choice`.
- `correct_answers` sempre es una array. En preguntes obertes pot contenir mes d'una resposta valida.
- En preguntes `multiple_choice`, totes les respostes correctes han d'existir dins `options`.
- L'ordre de `options` no cal barrejar-lo al JSON: la web el barreja cada vegada que mostra l'exercici.
