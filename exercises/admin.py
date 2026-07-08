from django.contrib import admin

from .models import Answer, Attempt, Category, Exercise, PimPam, Question, StudentPimPam, StudentProfile


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["__str__", "category", "level", "kind", "created_at"]
    list_filter = ["category", "level", "kind"]
    search_fields = ["title", "statement"]
    inlines = [QuestionInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["username", "created_at"]
    search_fields = ["username"]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ["exercise", "student", "score", "created_at"]
    list_filter = ["created_at"]


@admin.register(PimPam)
class PimPamAdmin(admin.ModelAdmin):
    list_display = ["name", "animal", "rarity"]
    list_filter = ["rarity", "animal"]
    search_fields = ["name", "animal"]


@admin.register(StudentPimPam)
class StudentPimPamAdmin(admin.ModelAdmin):
    list_display = ["student", "pimpam", "awarded_at"]
    list_filter = ["pimpam__rarity", "awarded_at"]
    search_fields = ["student__username", "pimpam__name"]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["attempt", "question", "is_correct"]
    list_filter = ["is_correct"]
