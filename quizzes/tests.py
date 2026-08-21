from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import CustomUser
from roadmaps.models import Roadmap, Step, StudentProgress
from .models import Choice, Question, Quiz, QuizAttempt


class QuizSubmissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="quizstudent",
            email="quizstudent@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.client.force_authenticate(user=self.user)

        self.roadmap = Roadmap.objects.create(
            title="Roadmap One",
            description="Roadmap description",
            created_by=self.user,
            status="published",
        )
        self.step = Step.objects.create(
            roadmap=self.roadmap,
            instructor=self.user,
            title="Step One",
            order=1,
            difficulty="beginner",
            unlock_score=80,
        )
        self.quiz = Quiz.objects.create(title="Quiz One", step=self.step)

        self.question_one = Question.objects.create(
            quiz=self.quiz,
            text="What is 2 + 2?",
            order=1,
        )
        self.choice_one = Choice.objects.create(
            question=self.question_one,
            text="4",
            is_correct=True,
        )
        self.choice_two = Choice.objects.create(
            question=self.question_one,
            text="5",
            is_correct=False,
        )

        self.question_two = Question.objects.create(
            quiz=self.quiz,
            text="What is 3 + 3?",
            order=2,
        )
        self.choice_three = Choice.objects.create(
            question=self.question_two,
            text="6",
            is_correct=True,
        )
        self.choice_four = Choice.objects.create(
            question=self.question_two,
            text="7",
            is_correct=False,
        )

    def test_create_quiz_attempt_returns_201(self):
        response = self.client.post(
            reverse("quiz-attempt-list"),
            {"quiz": self.quiz.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quiz"], self.quiz.pk)
        self.assertEqual(response.data["student"], self.user.pk)

    def test_submit_quiz_returns_score_and_pass_status(self):
        response = self.client.post(
            reverse("quiz-submit", kwargs={"pk": self.quiz.pk}),
            {
                "answers": [
                    {
                        "question": self.question_one.pk,
                        "choice": self.choice_one.pk,
                    },
                    {
                        "question": self.question_two.pk,
                        "choice": self.choice_three.pk,
                    },
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_questions"], 2)
        self.assertEqual(response.data["quiz"], self.quiz.pk)
        self.assertTrue(response.data["passed"])

        attempt = QuizAttempt.objects.get(student=self.user, quiz=self.quiz)
        self.assertEqual(attempt.attempt_number, 1)
        self.assertEqual(attempt.score, 100)

    def test_passing_a_quiz_completes_its_step_and_unlocks_the_next_one(self):
        next_step = Step.objects.create(
            roadmap=self.roadmap,
            instructor=self.user,
            title="Step Two",
            order=2,
            difficulty="beginner",
            unlock_score=80,
        )

        response = self.client.post(
            reverse("quiz-submit", kwargs={"pk": self.quiz.pk}),
            {
                "answers": [
                    {"question": self.question_one.pk, "choice": self.choice_one.pk},
                    {"question": self.question_two.pk, "choice": self.choice_three.pk},
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            StudentProgress.objects.get(student=self.user, step=self.step).status,
            "completed",
        )
        self.assertEqual(
            StudentProgress.objects.get(student=self.user, step=next_step).status,
            "active",
        )

    def test_instructor_can_create_quiz_with_step(self):
        instructor = get_user_model().objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="StrongPass123!",
            role="instructor",
        )
        self.client.force_authenticate(user=instructor)

        response = self.client.post(
            reverse("quiz-list"),
            {"title": "New Quiz", "step": self.step.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Quiz")
        self.assertEqual(response.data["step"], self.step.pk)

    def test_instructor_can_create_question_with_choices(self):
        instructor = get_user_model().objects.create_user(
            username="questionauthor",
            email="questionauthor@example.com",
            password="StrongPass123!",
            role="instructor",
        )
        self.client.force_authenticate(user=instructor)

        response = self.client.post(
            reverse("question-list"),
            {
                "quiz": self.quiz.pk,
                "text": "What is 5 + 5?",
                "order": 3,
                "choices": [
                    {"text": "10", "is_correct": True},
                    {"text": "11", "is_correct": False},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "What is 5 + 5?")
        self.assertEqual(response.data["quiz"], self.quiz.pk)
        self.assertEqual(len(response.data["choices"]), 2)
