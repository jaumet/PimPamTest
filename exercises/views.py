from decimal import Decimal
import json
from math import isqrt
import random

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import Count
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ExerciseForm, ExerciseImportForm, QuestionForm, StudentLoginForm
from .gamification import award_pimpam_for_attempt
from .importer import import_exercises
from .models import Answer, Attempt, Category, Exercise, PimPam, Question, StudentPimPam, StudentProfile


def current_student(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return None
    return StudentProfile.objects.filter(pk=student_id).first()


def recommended_exercises_for_student(student, limit=6, selected_groups=None):
    if not student:
        return []
    last_done_at = {}
    attempts = Attempt.objects.filter(student=student).order_by("-created_at")
    for attempt in attempts:
        last_done_at.setdefault(attempt.exercise_id, attempt.created_at)

    exercises = list(Exercise.objects.select_related("category").all())

    def sort_key(exercise):
        return (
            exercise.pk in last_done_at,
            last_done_at.get(exercise.pk),
            exercise.category.name,
            exercise.level,
            exercise.title or "",
        )

    if not selected_groups:
        exercises.sort(key=sort_key)
        return exercises[:limit]

    selected_group_set = set(selected_groups)
    selected_exercises = [
        exercise
        for exercise in exercises
        if (exercise.category_id, exercise.level) in selected_group_set
    ]
    by_group = {}
    for exercise in selected_exercises:
        by_group.setdefault((exercise.category_id, exercise.level), []).append(exercise)
    for group_exercises in by_group.values():
        group_exercises.sort(key=sort_key)

    recommended = []
    seen = set()
    for group in selected_groups:
        group_exercises = by_group.get(group, [])
        if group_exercises:
            exercise = group_exercises[0]
            recommended.append(exercise)
            seen.add(exercise.pk)
        if len(recommended) >= limit:
            return recommended

    selected_exercises.sort(key=sort_key)
    for exercise in selected_exercises:
        if exercise.pk not in seen:
            recommended.append(exercise)
            seen.add(exercise.pk)
        if len(recommended) >= limit:
            break
    return recommended


def parse_selected_content(values):
    selected_groups = []
    for value in values:
        try:
            category_id, level = value.split(":", 1)
            selected_groups.append((int(category_id), int(level)))
        except (TypeError, ValueError):
            continue
    return selected_groups


def summarize_import_payload(payload):
    summary = {
        "exercise_count": len(payload),
        "question_count": 0,
        "open_question_count": 0,
        "choice_question_count": 0,
        "categories": {},
        "levels": {},
        "exercises": [],
    }
    for item in payload:
        questions = item.get("questions", [])
        category_data = item.get("category") or {}
        category_name = category_data.get("name") or item.get("category_name") or "General"
        level = item.get("level", 1)
        summary["question_count"] += len(questions)
        summary["categories"][category_name] = summary["categories"].get(category_name, 0) + 1
        summary["levels"][level] = summary["levels"].get(level, 0) + 1
        for question in questions:
            if question.get("kind") == Question.QuestionKind.MULTIPLE_CHOICE:
                summary["choice_question_count"] += 1
            else:
                summary["open_question_count"] += 1
        summary["exercises"].append(
            {
                "title": item.get("title") or "Exercici sense titol",
                "category": category_name,
                "level": level,
                "question_count": len(questions),
            }
        )
    summary["categories"] = sorted(summary["categories"].items())
    summary["levels"] = sorted(summary["levels"].items())
    return summary


def home(request):
    student = current_student(request)
    selected_content_values = request.GET.getlist("content")
    selected_groups = parse_selected_content(selected_content_values)
    done_counts = {}
    student_attempts = []
    if student:
        student_attempts = list(
            Attempt.objects.filter(student=student).select_related("exercise", "exercise__category")
        )
        done_counts = dict(
            Attempt.objects.filter(student=student)
            .values("exercise_id")
            .annotate(total=Count("id"))
            .values_list("exercise_id", "total")
        )

    category_tree = []
    categories = Category.objects.prefetch_related("exercises").order_by("name")
    for category in categories:
        levels = {}
        for exercise in category.exercises.all():
            levels.setdefault(exercise.level, []).append(
                {"exercise": exercise, "done_count": done_counts.get(exercise.pk, 0)}
            )
        exercise_count = sum(len(exercises) for exercises in levels.values())
        done_count = sum(
            1
            for exercises in levels.values()
            for exercise_node in exercises
            if exercise_node["done_count"]
        )
        category_tree.append(
            {
                "category": category,
                "exercise_count": exercise_count,
                "done_count": done_count,
                "levels": [
                    {
                        "level": level,
                        "exercise_count": len(exercises),
                        "done_count": sum(1 for exercise_node in exercises if exercise_node["done_count"]),
                        "exercises": exercises,
                    }
                    for level, exercises in sorted(levels.items())
                ],
            }
        )

    content_selector = [
        {
            "category": node["category"],
            "levels": [
                {
                    "level": level["level"],
                    "exercise_count": level["exercise_count"],
                    "value": f"{node['category'].pk}:{level['level']}",
                    "selected": f"{node['category'].pk}:{level['level']}" in selected_content_values,
                }
                for level in node["levels"]
            ],
        }
        for node in category_tree
    ]

    recommended_exercises = []
    average_score = None
    collection_items = []
    collection_count = 0
    pimpam_catalog = []
    pimpam_summary = []
    star_total = 0
    attempt_waffle = []
    attempt_waffle_rows = 1
    category_legend = []
    star_waffle = []
    total_pimpams = PimPam.objects.count()
    if not student:
        pimpam_catalog = [{"pimpam": pimpam} for pimpam in PimPam.objects.all()]
    if student:
        recommended_exercises = recommended_exercises_for_student(student, selected_groups=selected_groups)

        category_colors = {}
        category_names = {}
        palette = ["#1f7a8c", "#e76f51", "#7b2cbf", "#2a9d8f", "#f4a261", "#457b9d", "#d62828", "#6a994e"]
        for attempt in reversed(student_attempts):
            category = attempt.exercise.category
            category_colors.setdefault(category.pk, palette[len(category_colors) % len(palette)])
            category_names[category.pk] = category.name
            score = float(attempt.score)
            attempt_waffle.append(
                {
                    "attempt": attempt,
                    "category_color": category_colors[category.pk],
                    "score_percent": f"{score:.0f}%",
                }
            )
        attempt_waffle_rows = max(1, isqrt(len(attempt_waffle)))
        category_legend = [
            {"name": category_names[category_id], "color": color}
            for category_id, color in category_colors.items()
        ]
        if student_attempts:
            average_score = sum(float(attempt.score) for attempt in student_attempts) / len(student_attempts)
        collection_items = list(
            StudentPimPam.objects.filter(student=student).select_related("pimpam", "attempt", "attempt__exercise")
        )
        star_total = sum(item.pimpam.rarity for item in collection_items)
        star_waffle = range(star_total)
        owned_by_pimpam = {}
        for item in collection_items:
            owned_by_pimpam.setdefault(item.pimpam_id, []).append(item)
        collection_count = len(owned_by_pimpam)
        pimpam_summary = [
            {
                "rarity": rarity,
                "pimpams": sorted(
                    {
                        item.pimpam
                        for item in collection_items
                        if item.pimpam.rarity == rarity
                    },
                    key=lambda pimpam: pimpam.name,
                ),
                "owned_count": len(
                    {
                        item.pimpam_id
                        for item in collection_items
                        if item.pimpam.rarity == rarity
                    }
                ),
                "award_count": sum(1 for item in collection_items if item.pimpam.rarity == rarity),
            }
            for rarity in range(5, 0, -1)
        ]
        pimpam_catalog = []
        for pimpam in PimPam.objects.all():
            awards = owned_by_pimpam.get(pimpam.pk, [])
            pimpam_catalog.append(
                {
                    "pimpam": pimpam,
                    "awards": awards,
                    "is_owned": bool(awards),
                    "award_count": len(awards),
                    "latest_award": awards[0] if awards else None,
                }
            )
        pimpam_catalog.sort(key=lambda item: (not item["is_owned"], item["pimpam"].rarity, item["pimpam"].name))

    default_tab = "exercises" if student else "pimpams"
    allowed_tabs = {"exercises", "results", "categories", "pimpams"} if student else {"pimpams", "categories"}
    active_tab = request.GET.get("tab", default_tab)
    if active_tab not in allowed_tabs:
        active_tab = default_tab

    return render(
        request,
        "exercises/home.html",
        {
            "active_tab": active_tab,
            "average_score": average_score,
            "category_tree": category_tree,
            "attempt_waffle": attempt_waffle,
            "attempt_waffle_rows": attempt_waffle_rows,
            "collection_count": collection_count,
            "category_legend": category_legend,
            "pimpam_catalog": pimpam_catalog,
            "pimpam_summary": pimpam_summary,
            "recommended_exercises": recommended_exercises,
            "content_selector": content_selector,
            "has_content_selection": bool(selected_groups),
            "star_waffle": star_waffle,
            "student": student,
            "student_attempts": student_attempts,
            "star_total": star_total,
            "total_pimpams": total_pimpams,
        },
    )


def student_access(request):
    active_student = current_student(request)
    form = StudentLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        code = form.cleaned_data["access_code"]
        student = StudentProfile.objects.filter(username=username).first()
        if student and student.access_code == code:
            request.session["student_id"] = student.pk
            messages.success(request, f"Ara ets {student.username}.")
            return redirect("home")
        if student:
            form.add_error("access_code", "Aquest numero no coincideix amb aquest nom.")
        else:
            student = StudentProfile.objects.create(username=username, access_code=code)
            request.session["student_id"] = student.pk
            messages.success(request, f"Ara ets {student.username}.")
            return redirect("home")
    return render(request, "exercises/student_access.html", {"form": form, "active_student": active_student})


def student_logout(request):
    request.session.pop("student_id", None)
    return redirect("home")


def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise.objects.prefetch_related("questions"), pk=pk)
    previous_exercise, next_exercise = sibling_exercises(exercise)
    questions = list(exercise.questions.all())
    statement_text = exercise.statement
    instruction_text = ""
    if len(questions) == 1:
        statement_text = questions[0].prompt
        instruction_text = exercise.statement

    question_nodes = []
    for question in questions:
        options = list(question.options)
        if question.kind == Question.QuestionKind.MULTIPLE_CHOICE:
            random.SystemRandom().shuffle(options)
        question_nodes.append({"question": question, "options": options})

    return render(
        request,
        "exercises/exercise_detail.html",
        {
            "exercise": exercise,
            "instruction_text": instruction_text,
            "next_exercise": next_exercise,
            "previous_exercise": previous_exercise,
            "question_nodes": question_nodes,
            "statement_text": statement_text,
        },
    )


def sibling_exercises(exercise):
    exercise_ids = list(
        Exercise.objects.order_by("category__name", "level", "id").values_list("id", flat=True)
    )
    current_index = exercise_ids.index(exercise.pk)
    previous_exercise = Exercise.objects.filter(pk=exercise_ids[current_index - 1]).first() if current_index > 0 else None
    next_exercise = (
        Exercise.objects.filter(pk=exercise_ids[current_index + 1]).first()
        if current_index < len(exercise_ids) - 1
        else None
    )
    return previous_exercise, next_exercise


@require_http_methods(["POST"])
@transaction.atomic
def submit_exercise(request, pk):
    exercise = get_object_or_404(Exercise.objects.prefetch_related("questions"), pk=pk)
    if not request.session.session_key:
        request.session.create()

    questions = list(exercise.questions.all())
    attempt = Attempt.objects.create(
        student=current_student(request),
        session_key=request.session.session_key or "",
        exercise=exercise,
        total_count=len(questions),
    )
    correct_count = 0
    for question in questions:
        answer = request.POST.get(f"question_{question.pk}", "")
        is_correct = question.is_correct(answer)
        correct_count += int(is_correct)
        Answer.objects.create(attempt=attempt, question=question, raw_answer=answer, is_correct=is_correct)

    attempt.correct_count = correct_count
    attempt.score = Decimal(correct_count * 100) / Decimal(len(questions) or 1)
    attempt.save(update_fields=["correct_count", "score"])
    award_pimpam_for_attempt(attempt)
    return redirect("attempt_result", pk=attempt.pk)


def attempt_result(request, pk):
    attempt = get_object_or_404(
        Attempt.objects.select_related("exercise", "pimpam_award__pimpam").prefetch_related("answers__question"), pk=pk
    )
    previous_exercise, result_next_exercise = sibling_exercises(attempt.exercise)
    next_exercise = None
    if attempt.student:
        for exercise in recommended_exercises_for_student(attempt.student):
            if exercise.pk != attempt.exercise_id:
                next_exercise = exercise
                break

    display_pimpam = None
    is_saved_award = False
    if hasattr(attempt, "pimpam_award"):
        display_pimpam = attempt.pimpam_award.pimpam
        is_saved_award = True
    elif attempt.score > 0:
        max_rarity = 1
        if attempt.score >= 90:
            max_rarity = 5
        elif attempt.score >= 75:
            max_rarity = 4
        elif attempt.score >= 50:
            max_rarity = 3
        elif attempt.score >= 25:
            max_rarity = 2
        candidates = list(PimPam.objects.filter(rarity__lte=max_rarity).order_by("rarity", "name"))
        if candidates:
            display_pimpam = candidates[(attempt.pk + int(attempt.score)) % len(candidates)]

    return render(
        request,
        "exercises/attempt_result.html",
        {
            "attempt": attempt,
            "display_pimpam": display_pimpam,
            "is_saved_award": is_saved_award,
            "next_exercise": next_exercise,
            "previous_exercise": previous_exercise,
            "result_next_exercise": result_next_exercise,
        },
    )


@staff_member_required
def exercise_create(request):
    QuestionFormSet = modelformset_factory(Question, form=QuestionForm, extra=3, can_delete=False)
    exercise_form = ExerciseForm(request.POST or None)
    formset = QuestionFormSet(request.POST or None, queryset=Question.objects.none())
    if request.method == "POST" and exercise_form.is_valid() and formset.is_valid():
        with transaction.atomic():
            exercise = exercise_form.save()
            for form in formset:
                if form.cleaned_data:
                    question = form.save(commit=False)
                    question.exercise = exercise
                    question.full_clean()
                    question.save()
        messages.success(request, "Exercici creat.")
        return redirect(exercise)
    return render(request, "exercises/exercise_form.html", {"exercise_form": exercise_form, "formset": formset})


@staff_member_required
def exercise_import(request):
    if request.method == "POST" and request.POST.get("confirm_import") == "1":
        payload = request.session.get("exercise_import_payload")
        if not payload:
            messages.error(request, "No hi ha cap JSON pendent de confirmar.")
            return redirect("exercise_import")
        created = import_exercises(payload)
        request.session.pop("exercise_import_payload", None)
        messages.success(request, f"S'han importat {len(created)} exercicis.")
        return redirect("admin:exercises_exercise_changelist")

    form = ExerciseImportForm(request.POST or None, request.FILES or None)
    preview = None
    if request.method == "POST" and form.is_valid():
        payload = form.cleaned_data["parsed_json"]
        request.session["exercise_import_payload"] = json.loads(json.dumps(payload))
        preview = summarize_import_payload(payload)
    return render(request, "exercises/exercise_import.html", {"form": form, "preview": preview})
