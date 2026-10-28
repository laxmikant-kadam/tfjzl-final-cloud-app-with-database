import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Course, Enrollment, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)

# A learner needs more than this percentage to pass the mock exam.
PASSING_GRADE = 80


def registration_request(request):
    """Show the sign-up form and create a new user account on POST."""
    context = {}
    if request.method == "GET":
        return render(request, "onlinecourse/user_registration_bootstrap.html", context)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("psw", "")
        first_name = request.POST.get("firstname", "").strip()
        last_name = request.POST.get("lastname", "").strip()

        if not username or not password:
            context["message"] = "User name and password are required."
            return render(request, "onlinecourse/user_registration_bootstrap.html", context)

        if User.objects.filter(username=username).exists():
            context["message"] = "User already exists."
            return render(request, "onlinecourse/user_registration_bootstrap.html", context)

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        login(request, user)
        return redirect("onlinecourse:index")

    return render(request, "onlinecourse/user_registration_bootstrap.html", context)


def login_request(request):
    """Authenticate a user and start a session."""
    context = {}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("psw", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("onlinecourse:index")

        context["message"] = "Invalid username or password."
        return render(request, "onlinecourse/user_login_bootstrap.html", context)

    return render(request, "onlinecourse/user_login_bootstrap.html", context)


def logout_request(request):
    """End the current session."""
    logout(request)
    return redirect("onlinecourse:index")


def check_if_enrolled(user, course):
    """Return True when the given user is enrolled in the given course."""
    if user.is_authenticated:
        return Enrollment.objects.filter(user=user, course=course).exists()
    return False


class CourseListView(generic.ListView):
    """List the most popular courses on the home page."""

    template_name = "onlinecourse/course_list_bootstrap.html"
    context_object_name = "course_list"

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.prefetch_related("instructors").order_by(
            "-total_enrollment", "name"
        )[:10]
        for course in courses:
            course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    """Show the course name, its lessons and (for enrolled users) the mock exam."""

    model = Course
    template_name = "onlinecourse/course_details_bootstrap.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        context["is_enrolled"] = check_if_enrolled(user, course)
        context["questions"] = course.question_set.prefetch_related("choice_set")
        context["lessons"] = course.lesson_set.all()
        return context


@login_required
def enroll(request, course_id):
    """Enroll the current user in a course."""
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    if not check_if_enrolled(user, course):
        Enrollment.objects.create(user=user, course=course, mode=Enrollment.HONOR)
        course.total_enrollment = Enrollment.objects.filter(course=course).count()
        course.save(update_fields=["total_enrollment"])

    return redirect("onlinecourse:course_details", pk=course.id)


def extract_answers(request):
    """Collect the selected choice ids from the submitted exam form."""
    submitted_answers = []
    for key in request.POST:
        if key.startswith("choice"):
            try:
                submitted_answers.append(int(request.POST[key]))
            except (TypeError, ValueError):
                logger.warning("Ignoring non-numeric exam answer: %s", request.POST[key])
    return submitted_answers


@login_required
def submit(request, course_id):
    """Create a Submission for the learner's enrollment and grade it."""
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

    if enrollment is None:
        # The learner must enroll before taking the exam.
        return redirect("onlinecourse:course_details", pk=course.id)

    submission = Submission.objects.create(enrollment=enrollment)

    selected_ids = extract_answers(request)
    # Only accept choices that actually belong to this course's exam.
    valid_choice_ids = Choice.objects.filter(
        question__course=course, id__in=selected_ids
    ).values_list("id", flat=True)
    submission.choices.add(*valid_choice_ids)

    return redirect(
        "onlinecourse:show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    """Grade a submission and display the exam results."""
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission.objects.select_related("enrollment__user"),
        pk=submission_id,
        enrollment__course=course,
    )

    # A learner may only see their own results; staff can review any attempt.
    if not request.user.is_staff and submission.enrollment.user_id != request.user.id:
        raise PermissionDenied("You can only view your own exam results.")

    selected_ids = list(submission.choices.values_list("id", flat=True))
    questions = course.question_set.prefetch_related("choice_set")

    max_score = 0
    total_score = 0
    results = []
    for question in questions:
        earned = question.get_score(selected_ids)
        max_score += question.question_point
        total_score += earned
        results.append(
            {
                "question": question,
                "earned": earned,
                "is_correct": earned == question.question_point,
            }
        )

    grade = int(round(total_score / max_score * 100)) if max_score else 0

    attempt_number = Submission.objects.filter(
        enrollment=submission.enrollment, id__lte=submission.id
    ).count()

    context = {
        "course": course,
        "submission": submission,
        "attempt_number": attempt_number,
        "selected_ids": selected_ids,
        "questions": questions,
        "results": results,
        "total_score": total_score,
        "max_score": max_score,
        "grade": grade,
        "passed": grade >= PASSING_GRADE,
        "passing_grade": PASSING_GRADE,
    }
    return render(request, "onlinecourse/exam_result_bootstrap.html", context)
