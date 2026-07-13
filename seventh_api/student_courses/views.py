from datetime import datetime
from typing import Any

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema

from .models import Course, Enrollment, ExamResult, Student


api = NinjaAPI(title="Student Course Management API", version="1.0.0")


class StudentIn(Schema):
    name: str
    email: str


class StudentUpdate(Schema):
    name: str | None = None
    email: str | None = None


class StudentOut(Schema):
    id: int
    name: str
    email: str


class CourseIn(Schema):
    title: str
    description: str


class CourseUpdate(Schema):
    title: str | None = None
    description: str | None = None


class CourseOut(Schema):
    id: int
    title: str
    description: str


class EnrollmentIn(Schema):
    student_id: int
    course_id: int


class EnrollmentOut(Schema):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime


class ExamResultIn(Schema):
    student_id: int
    course_id: int
    grade: float


class ExamResultOut(Schema):
    id: int
    student_id: int
    course_id: int
    grade: float
    created_at: datetime


class CourseAverageOut(Schema):
    course_id: int
    average_grade: float | None


@api.get("/students", response=list[StudentOut])
@login_required
def list_students(request: HttpRequest) -> Any:
    """Return all students."""
    return Student.objects.all()


@api.post("/students", response=StudentOut)
@login_required
def create_student(request: HttpRequest, payload: StudentIn) -> Any:
    """Create a new student."""
    return Student.objects.create(**payload.dict())


@api.get("/students/{student_id}", response=StudentOut)
@login_required
def get_student(request: HttpRequest, student_id: int) -> Any:
    """Return a single student by ID."""
    return get_object_or_404(Student, id=student_id)


@api.put("/students/{student_id}", response=StudentOut)
@login_required
def update_student(request: HttpRequest, student_id: int, payload: StudentIn) -> Any:
    """Replace a student."""
    student = get_object_or_404(Student, id=student_id)
    for attr, value in payload.dict().items():
        setattr(student, attr, value)
    student.save()
    return student


@api.patch("/students/{student_id}", response=StudentOut)
@login_required
def patch_student(
    request: HttpRequest,
    student_id: int,
    payload: StudentUpdate,
) -> Any:
    """Partially update a student."""
    student = get_object_or_404(Student, id=student_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(student, attr, value)
    student.save()
    return student


@api.delete("/students/{student_id}")
@login_required
def delete_student(request: HttpRequest, student_id: int) -> dict[str, bool]:
    """Delete a student."""
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return {"success": True}


@api.get("/courses", response=list[CourseOut])
@login_required
def list_courses(request: HttpRequest) -> Any:
    """Return all courses."""
    return Course.objects.all()


@api.post("/courses", response=CourseOut)
@login_required
def create_course(request: HttpRequest, payload: CourseIn) -> Any:
    """Create a new course."""
    return Course.objects.create(**payload.dict())


@api.get("/courses/{course_id}", response=CourseOut)
@login_required
def get_course(request: HttpRequest, course_id: int) -> Any:
    """Return a single course by ID."""
    return get_object_or_404(Course, id=course_id)


@api.put("/courses/{course_id}", response=CourseOut)
@login_required
def update_course(request: HttpRequest, course_id: int, payload: CourseIn) -> Any:
    """Replace a course."""
    course = get_object_or_404(Course, id=course_id)
    for attr, value in payload.dict().items():
        setattr(course, attr, value)
    course.save()
    return course


@api.patch("/courses/{course_id}", response=CourseOut)
@login_required
def patch_course(
    request: HttpRequest,
    course_id: int,
    payload: CourseUpdate,
) -> Any:
    """Partially update a course."""
    course = get_object_or_404(Course, id=course_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(course, attr, value)
    course.save()
    return course


@api.delete("/courses/{course_id}")
@login_required
def delete_course(request: HttpRequest, course_id: int) -> dict[str, bool]:
    """Delete a course."""
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return {"success": True}


@api.get("/enrollments", response=list[EnrollmentOut])
@login_required
def list_enrollments(request: HttpRequest) -> Any:
    """Return all course enrollments."""
    return Enrollment.objects.all()


@api.post("/enrollments", response=EnrollmentOut)
@login_required
def enroll_student(request: HttpRequest, payload: EnrollmentIn) -> Any:
    """Enroll a student in a course."""
    get_object_or_404(Student, id=payload.student_id)
    get_object_or_404(Course, id=payload.course_id)
    enrollment, _ = Enrollment.objects.get_or_create(
        student_id=payload.student_id,
        course_id=payload.course_id,
    )
    return enrollment


@api.get("/exam-results", response=list[ExamResultOut])
@login_required
def list_exam_results(
    request: HttpRequest,
    student_id: int = None,
    course_id: int = None,
) -> Any:
    """Return exam results filtered by student or course."""
    results = ExamResult.objects.all()

    if student_id:
        results = results.filter(student_id=student_id)

    if course_id:
        results = results.filter(course_id=course_id)

    return results


@api.post("/exam-results", response=ExamResultOut)
@login_required
def create_exam_result(request: HttpRequest, payload: ExamResultIn) -> Any:
    """Create an exam result for an enrolled student."""
    get_object_or_404(
        Enrollment,
        student_id=payload.student_id,
        course_id=payload.course_id,
    )
    return ExamResult.objects.create(**payload.dict())


@api.get("/courses/{course_id}/average-grade", response=CourseAverageOut)
@login_required
def get_course_average_grade(
    request: HttpRequest,
    course_id: int,
) -> dict[str, float | int | None]:
    """Return the average grade for a course."""
    get_object_or_404(Course, id=course_id)
    average_grade = ExamResult.objects.filter(course_id=course_id).aggregate(
        average=Avg("grade")
    )["average"]
    return {"course_id": course_id, "average_grade": average_grade}
