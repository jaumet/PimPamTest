from django.db import transaction
from django.utils.text import slugify

from .models import Category, Exercise, Question


@transaction.atomic
def import_exercises(payload):
    created = []
    for item in payload:
        category_data = item.get("category") or {}
        category_name = category_data.get("name") or item.get("category_name") or "General"
        category_slug = category_data.get("slug") or slugify(category_name)
        category, _ = Category.objects.get_or_create(
            slug=category_slug,
            defaults={"name": category_name, "description": category_data.get("description", "")},
        )

        exercise = Exercise.objects.create(
            title=item.get("title", ""),
            statement=item["statement"],
            image=item.get("image", ""),
            category=category,
            level=item.get("level", 1),
            kind=item.get("kind", Exercise.ExerciseKind.OPEN_THREE),
            feedback=item.get("feedback", ""),
        )
        for index, question_data in enumerate(item.get("questions", []), start=1):
            question = Question(
                exercise=exercise,
                prompt=question_data["prompt"],
                kind=question_data.get("kind", Question.QuestionKind.OPEN),
                order=question_data.get("order", index),
                options=question_data.get("options", []),
                correct_answers=question_data["correct_answers"],
                explanation=question_data.get("explanation", ""),
            )
            question.full_clean()
            question.save()
        created.append(exercise)
    return created
