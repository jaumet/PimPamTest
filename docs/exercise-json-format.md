# Format JSON d'exercicis

El fitxer d'importacio ha de ser una array d'exercicis.

```json
[
  {
    "title": "Comprensio lectora 1",
    "statement": "Llegeix el text i respon les preguntes.",
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

Valors admesos:

- `kind` d'exercici: `open_three` o `multiple_choice`.
- `level`: nivell numeric de l'exercici. Si no s'indica, es desa com a `1`.
- `kind` de pregunta: `open` o `multiple_choice`.
- `correct_answers` sempre es una array. En preguntes obertes pot contenir mes d'una resposta valida.
- En preguntes `multiple_choice`, totes les respostes correctes han d'existir dins `options`.
