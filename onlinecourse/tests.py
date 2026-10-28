from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Choice, Course, Enrollment, Question, Submission


class ExamFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="learner", password="secret123", first_name="Ada"
        )
        self.course = Course.objects.create(
            name="Test Course", description="A course used by the tests."
        )
        self.lesson = self.course.lesson_set.create(
            title="First lesson", order=1, content="Lesson content"
        )
        self.question = Question.objects.create(
            course=self.course,
            question_text="What is Django?",
            grade=10,
        )
        self.correct = Choice.objects.create(
            question=self.question, choice_text="A web framework", is_correct=True
        )
        self.wrong = Choice.objects.create(
            question=self.question, choice_text="A database", is_correct=False
        )

    def test_course_details_shows_name_and_lessons(self):
        response = self.client.get(
            reverse("onlinecourse:course_details", args=[self.course.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Course")
        self.assertContains(response, "First lesson")
        self.assertContains(response, "Lesson content")

    def test_submit_requires_enrollment(self):
        self.client.login(username="learner", password="secret123")
        response = self.client.post(
            reverse("onlinecourse:submit", args=[self.course.id]),
            {"choice_%s" % self.correct.id: self.correct.id},
        )
        self.assertRedirects(
            response,
            reverse("onlinecourse:course_details", args=[self.course.id]),
        )
        self.assertEqual(Submission.objects.count(), 0)

    def test_full_score_submission_shows_congratulations(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        self.client.login(username="learner", password="secret123")
        response = self.client.post(
            reverse("onlinecourse:submit", args=[self.course.id]),
            {
                "choice_%s" % self.correct.id: self.correct.id,
            },
            follow=True,
        )
        submission = Submission.objects.get()
        self.assertEqual(
            list(submission.choices.all()), [self.correct]
        )
        self.assertRedirects(
            response,
            reverse(
                "onlinecourse:show_exam_result",
                args=[self.course.id, submission.id],
            ),
        )
        self.assertContains(response, "Congratulations")
        self.assertContains(response, "10/10")
        self.assertContains(response, "100/100")

    def test_wrong_answer_scores_zero(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        self.client.login(username="learner", password="secret123")
        response = self.client.post(
            reverse("onlinecourse:submit", args=[self.course.id]),
            {"choice_%s" % self.wrong.id: self.wrong.id},
            follow=True,
        )
        self.assertContains(response, "Sorry")
        self.assertContains(response, "0/10")

    def test_other_user_cannot_view_results(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        submission = Submission.objects.create(
            enrollment=Enrollment.objects.get(user=self.user, course=self.course)
        )
        other = User.objects.create_user(username="other", password="secret123")
        self.client.login(username="other", password="secret123")
        response = self.client.get(
            reverse(
                "onlinecourse:show_exam_result",
                args=[self.course.id, submission.id],
            )
        )
        self.assertEqual(response.status_code, 403)
