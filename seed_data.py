"""Create demo users, a course with lessons and a mock exam.

Run it once after migrating:

    python seed_data.py
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.utils import timezone  # noqa: E402

from onlinecourse.models import (  # noqa: E402
    Choice,
    Course,
    Enrollment,
    Instructor,
    Learner,
    Lesson,
    Question,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COURSE_IMAGE = os.path.join(BASE_DIR, "media", "course_images", "django_course.png")


def create_course_image():
    """Draw a simple course banner so the ImageField has a real image."""
    from PIL import Image, ImageDraw, ImageFont

    os.makedirs(os.path.dirname(COURSE_IMAGE), exist_ok=True)
    width, height = 900, 420
    image = Image.new("RGB", (width, height), "#0d6efd")
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / height
        draw.line(
            [(0, y), (width, y)],
            fill=(
                int(13 + (32 - 13) * ratio),
                int(110 + (201 - 110) * ratio),
                int(253 + (151 - 253) * ratio),
            ),
        )
    try:
        title_font = ImageFont.load_default(size=52)
        subtitle_font = ImageFont.load_default(size=26)
    except TypeError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    draw.text((60, 150), "Django Application", font=title_font, fill="white")
    draw.text((60, 215), "Development", font=title_font, fill="white")
    draw.text(
        (62, 300),
        "OnlineCourse mock exam project",
        font=subtitle_font,
        fill="#e9f2ff",
    )
    image.save(COURSE_IMAGE, "PNG")


def create_user(username, password, first_name, last_name, is_staff=False, is_superuser=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{username}@example.com",
            "is_staff": is_staff,
            "is_superuser": is_superuser,
        },
    )
    if created:
        user.set_password(password)
        user.save()
    else:
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()
    return user


def main():
    create_course_image()

    admin = create_user(
        "admin", "Admin@12345", "Site", "Administrator", is_staff=True, is_superuser=True
    )
    instructor_user = create_user("instructor", "Instructor@123", "Grace", "Hopper")
    learner_user = create_user("john", "Learner@123", "John", "Doe")

    instructor, _ = Instructor.objects.get_or_create(
        user=instructor_user, defaults={"full_time": True, "total_learners": 1}
    )
    Learner.objects.get_or_create(
        user=learner_user, defaults={"occupation": Learner.STUDENT, "social_link": ""}
    )

    # Rebuild the demo course so the script can be run repeatedly.
    Course.objects.filter(name="Django Application Development").delete()
    course = Course.objects.create(
        name="Django Application Development",
        description=(
            "Learn how to build database-backed web applications with Django: "
            "models, the admin site, views, URLs, templates and a mock exam."
        ),
        pub_date=timezone.localdate(),
        image="course_images/django_course.png",
    )
    course.instructors.add(instructor)

    lessons = [
        (
            1,
            "Introduction to Django",
            "Django is a high-level Python web framework that encourages rapid "
            "development and clean, pragmatic design. A project can contain many "
            "apps, and each app groups related models, views and templates.",
        ),
        (
            2,
            "Models and Databases",
            "Models describe the data of an application. Each model maps to a "
            "database table, and fields map to columns. Migrations keep the "
            "database schema in sync with the models.",
        ),
        (
            3,
            "Views, URLs and Templates",
            "A URL pattern sends a request to a view. The view prepares data and "
            "renders a template, which uses Django template tags such as for and "
            "if to display the data.",
        ),
        (
            4,
            "The Django Admin Site",
            "The admin site is a ready-made interface for managing data. Register "
            "models with admin.site.register and customise the forms with inline "
            "classes and ModelAdmin options.",
        ),
    ]
    lesson_objects = []
    for order, title, content in lessons:
        lesson_objects.append(
            Lesson.objects.create(
                course=course, order=order, title=title, content=content
            )
        )
    questions = [
        (
            "Which command applies the migrations and creates the database tables?",
            10,
            [
                ("python manage.py migrate", True),
                ("python manage.py runserver", False),
                ("python manage.py startapp", False),
                ("python manage.py collectstatic", False),
            ],
        ),
        (
            "Which file maps URL patterns to the views that handle them?",
            10,
            [
                ("urls.py", True),
                ("models.py", False),
                ("admin.py", False),
                ("settings.py", False),
            ],
        ),
        (
            "What does the Django template tag {% for %} do?",
            10,
            [
                ("Loops over each item in a sequence", True),
                ("Includes another template", False),
                ("Loads a static file", False),
                ("Defines a URL pattern", False),
            ],
        ),
        (
            "Which field type links one Submission to many selected Choices?",
            10,
            [
                ("ManyToManyField", True),
                ("ForeignKey", False),
                ("OneToOneField", False),
                ("CharField", False),
            ],
        ),
    ]
    for order, (text, points, choices) in enumerate(questions, start=1):
        question = Question.objects.create(
            course=course,
            question_text=f"{text}",
            grade=points,
        )
        for choice_text, is_correct in choices:
            Choice.objects.create(
                question=question, choice_text=choice_text, is_correct=is_correct
            )

    Enrollment.objects.get_or_create(
        user=learner_user, course=course, defaults={"mode": Enrollment.HONOR}
    )
    course.total_enrollment = Enrollment.objects.filter(course=course).count()
    course.save(update_fields=["total_enrollment"])

    print("Demo data created.")
    print(f"  Admin:    {admin.username} / Admin@12345  (http://127.0.0.1:8000/admin/)")
    print(f"  Learner:  {learner_user.username} / Learner@123")
    print(f"  Course:   {course.name} (id={course.pk}) with {len(lessons)} lessons")


if __name__ == "__main__":
    main()
