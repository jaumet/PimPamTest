import json

from django import forms
from django.core.exceptions import ValidationError

from .models import Category, Exercise, Question, StudentProfile


class StudentLoginForm(forms.Form):
    username = forms.CharField(
        label="Nom",
        max_length=80,
        widget=forms.TextInput(attrs={"autocomplete": "off", "autofocus": True}),
    )
    access_code = forms.RegexField(
        label="Numero de 4 xifres",
        regex=r"^\d{4}$",
        max_length=4,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "inputmode": "numeric",
                "pattern": "[0-9]{4}",
                "maxlength": "4",
            }
        ),
    )

    def clean_username(self):
        return self.cleaned_data["username"].strip()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "description"]


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["title", "statement", "image", "category", "level", "kind", "feedback"]


class QuestionForm(forms.ModelForm):
    options_text = forms.CharField(
        label="Opcions",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Una opcio per linia. Nomes per preguntes tipus test.",
    )
    correct_answers_text = forms.CharField(
        label="Respostes correctes",
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Una resposta correcta per linia.",
    )

    class Meta:
        model = Question
        fields = ["prompt", "kind", "order", "options_text", "correct_answers_text", "explanation"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["options_text"].initial = "\n".join(map(str, self.instance.options))
            self.fields["correct_answers_text"].initial = "\n".join(map(str, self.instance.correct_answers))

    def clean(self):
        cleaned = super().clean()
        cleaned["options"] = [line.strip() for line in cleaned.get("options_text", "").splitlines() if line.strip()]
        cleaned["correct_answers"] = [
            line.strip() for line in cleaned.get("correct_answers_text", "").splitlines() if line.strip()
        ]
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.options = self.cleaned_data["options"]
        instance.correct_answers = self.cleaned_data["correct_answers"]
        if commit:
            instance.save()
        return instance


class ExerciseImportForm(forms.Form):
    json_file = forms.FileField(label="Fitxer JSON")

    def clean_json_file(self):
        uploaded = self.cleaned_data["json_file"]
        try:
            data = json.loads(uploaded.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValidationError("El fitxer ha de ser un JSON valid codificat en UTF-8.") from exc
        if not isinstance(data, list):
            raise ValidationError("El JSON ha de contenir una array d'exercicis.")
        uploaded.seek(0)
        self.cleaned_data["parsed_json"] = data
        return uploaded
