from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from roadmaps.permissions import IsInstructorOrAdmin

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from rest_framework.response import Response

from .models import Choice, Question, Quiz, QuizAttempt, StudentAnswer
from .serializers import (
    ChoiceSerializer,
    QuestionSerializer,
    QuizSerializer,
    QuizAttemptSerializer,
    StudentAnswerSerializer,
    SubmitQuizSerializer,
)
from .services import submit_quiz



class QuizListCreateView(generics.ListCreateAPIView):
    queryset = Quiz.objects.select_related("step").order_by("step")
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.select_related("step")
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]




class QuestionListCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.select_related(
        "quiz"
    ).order_by("quiz", "order")

    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.select_related("quiz")

    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]




class ChoiceListCreateView(generics.ListCreateAPIView):
    queryset = Choice.objects.select_related(
        "question"
    ).order_by("question", "id")

    serializer_class = ChoiceSerializer


    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]


class ChoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Choice.objects.select_related(
        "question"
    ).order_by("question", "id")

    serializer_class = ChoiceSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]




class QuizAttemptListCreateView(generics.ListCreateAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.select_related(
            "quiz",
            "student"
        ).filter(
            student=self.request.user
        ).order_by("-completed_at")

    def perform_create(self, serializer):
        quiz = serializer.validated_data["quiz"]

        last_attempt = QuizAttempt.objects.filter(
            student=self.request.user,
            quiz=quiz,
        ).order_by("-attempt_number").first()

        attempt_number = 1

        if last_attempt:
            attempt_number = last_attempt.attempt_number + 1

        serializer.save(
            student=self.request.user,
            quiz=quiz,
            attempt_number=attempt_number,
            score=0,
            passed=False,
        )


class QuizAttemptDetailView(generics.RetrieveAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
       return QuizAttempt.objects.select_related(
            "quiz",
            "student"
        ).filter(
            student=self.request.user
        )




class StudentAnswerListView(generics.ListAPIView):
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudentAnswer.objects.select_related(
            "attempt",
            "question",
            "choice"
        ).filter(
            attempt__student=self.request.user
        )


class StudentAnswerDetailView(generics.RetrieveAPIView):
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudentAnswer.objects.select_related(
            "attempt",
            "question",
            "choice"
        ).filter(
            attempt__student=self.request.user
        )
    

class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = SubmitQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = submit_quiz(
            student=request.user,
            quiz_id=pk,
            answers=serializer.validated_data["answers"],
        )

        return Response(result)