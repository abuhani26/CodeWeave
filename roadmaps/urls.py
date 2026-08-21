from django.urls import path

from .views import (
    CompleteStepView,
    LearningContentDetailView,
    LearningContentListCreateView,
    RoadmapDetailView,
    RoadmapListCreateView,
    StepDetailView,
    StepListCreateView,
    StudentProgressDetailView,
    StudentProgressListCreateView,
)

urlpatterns = [
    path("roadmaps/", RoadmapListCreateView.as_view(), name="roadmap-list"),
    path("roadmaps/<int:pk>/", RoadmapDetailView.as_view(), name="roadmap-detail"),
    path("roadmaps/<int:roadmap_id>/steps/", StepListCreateView.as_view(), name="roadmap-step-list"),
    path("steps/", StepListCreateView.as_view(), name="step-list-create"),
    path("steps/<int:pk>/", StepDetailView.as_view(), name="step-detail"),
    path("steps/<int:pk>/complete/", CompleteStepView.as_view(), name="step-complete"),
    path("contents/", LearningContentListCreateView.as_view(), name="learning-content-list-create"),
    path("steps/<int:step_id>/content/", LearningContentListCreateView.as_view()),
    path("contents/<int:pk>/", LearningContentDetailView.as_view(), name="learning-content-detail"),
    path("progress/", StudentProgressListCreateView.as_view(), name="student-progress-list-create"),
    path("progress/<int:pk>/", StudentProgressDetailView.as_view(), name="student-progress-detail"),
]
