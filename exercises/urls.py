from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("usuari/", views.student_access, name="student_access"),
    path("sortir/", views.student_logout, name="student_logout"),
    path("exercicis/nou/", views.exercise_create, name="exercise_create"),
    path("exercicis/importar/", views.exercise_import, name="exercise_import"),
    path("exercicis/netejar-duplicats/", views.exercise_dedupe, name="exercise_dedupe"),
    path("exercicis/<int:pk>/", views.exercise_detail, name="exercise_detail"),
    path("exercicis/<int:pk>/resoldre/", views.submit_exercise, name="submit_exercise"),
    path("resultats/<int:pk>/", views.attempt_result, name="attempt_result"),
]
