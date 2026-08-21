from django.urls import path
from .views import SubmitQuizView

from .views import (
    ChoiceDetailView,
    ChoiceListCreateView,
    QuestionDetailView,
    QuestionListCreateView,
    QuizAttemptDetailView,
    QuizAttemptListCreateView,
    QuizDetailView,
    QuizListCreateView,
    StudentAnswerDetailView,
    StudentAnswerListView,
)

urlpatterns = [
    path("", QuizListCreateView.as_view(), name="quiz-list"),
    path("<int:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("<int:pk>/submit/", SubmitQuizView.as_view(), name="quiz-submit"),

    path("questions/", QuestionListCreateView.as_view(), name="question-list"),
    path("questions/<int:pk>/", QuestionDetailView.as_view(), name="question-detail"),

    path("choices/", ChoiceListCreateView.as_view(), name="choice-list"),
    path("choices/<int:pk>/", ChoiceDetailView.as_view(), name="choice-detail"),

    path("attempts/", QuizAttemptListCreateView.as_view(), name="quiz-attempt-list"),
    path("attempts/<int:pk>/", QuizAttemptDetailView.as_view(), name="quiz-attempt-detail"),

    path("answers/", StudentAnswerListView.as_view(), name="student-answer-list"),
    path("answers/<int:pk>/", StudentAnswerDetailView.as_view(), name="student-answer-detail"),
]