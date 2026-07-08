from .models import StudentProfile


def active_student(request):
    student_id = request.session.get("student_id")
    student = StudentProfile.objects.filter(pk=student_id).first() if student_id else None
    return {"active_student": student}
