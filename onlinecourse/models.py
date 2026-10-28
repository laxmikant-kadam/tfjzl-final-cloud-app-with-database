from django.conf import settings
from django.db import models
from django.utils import timezone


class Instructor(models.Model):
    """A teacher who can be attached to one or more courses."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Learner(models.Model):
    """Extra profile information for a learner."""

    STUDENT = "student"
    DEVELOPER = "developer"
    DATA_SCIENTIST = "data_scientist"
    DATABASE_ADMIN = "dba"
    OCCUPATION_CHOICES = [
        (STUDENT, "Student"),
        (DEVELOPER, "Developer"),
        (DATA_SCIENTIST, "Data Scientist"),
        (DATABASE_ADMIN, "Database Admin"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    occupation = models.CharField(
        max_length=20, choices=OCCUPATION_CHOICES, default=STUDENT
    )
    social_link = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_occupation_display()})"


class Course(models.Model):
    """An online course made of lessons and an optional mock exam."""

    name = models.CharField(max_length=100, default="online course")
    image = models.ImageField(upload_to="course_images/", blank=True, null=True)
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(default=timezone.now)
    instructors = models.ManyToManyField(Instructor, blank=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Enrollment",
        related_name="enrolled_courses",
        blank=True,
    )
    total_enrollment = models.IntegerField(default=0)

    class Meta:
        ordering = ["-pub_date", "name"]

    def __str__(self):
        return self.name

    def is_enrolled_by(self, user):
        """Return True when ``user`` is enrolled in this course."""
        if not user.is_authenticated:
            return False
        return self.enrollment_set.filter(user=user).exists()


class Lesson(models.Model):
    """A single lesson that belongs to a course."""

    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Lesson {self.order}: {self.title}"


class Enrollment(models.Model):
    """Links a user to a course and is used to track exam submissions."""

    AUDIT = "audit"
    HONOR = "honor"
    BETA = "BETA"
    COURSE_MODES = [
        (AUDIT, "Audit"),
        (HONOR, "Honor"),
        (BETA, "BETA"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=timezone.now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.name}"


class Question(models.Model):
    """A single exam question. One question can be linked to many lessons."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lessons = models.ManyToManyField(Lesson, blank=True, related_name="questions")
    question_text = models.CharField(max_length=500)
    question_point = models.IntegerField(default=1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.question_text

    def correct_choice_ids(self):
        return set(
            self.choice_set.filter(is_correct=True).values_list("id", flat=True)
        )

    def get_score(self, selected_ids):
        """Return the points earned for this question.

        Full points are awarded only when the learner selects every correct
        choice for the question and no incorrect choice.
        """
        selected_ids = set(selected_ids)
        question_choice_ids = set(
            self.choice_set.values_list("id", flat=True)
        )
        correct_ids = self.correct_choice_ids()

        if not correct_ids:
            return 0
        if selected_ids & question_choice_ids == correct_ids:
            return self.question_point
        return 0


class Choice(models.Model):
    """One answer option for a question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    """A learner's exam attempt: an enrollment plus the selected choices."""

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at", "-id"]

    def __str__(self):
        return f"Submission #{self.pk} by {self.enrollment.user.username}"
