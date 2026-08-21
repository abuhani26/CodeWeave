from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView

from .permissions import IsInstructorOrAdmin

from .models import LearningContent, Roadmap, Step, StudentProgress
from .serializers import LearningContentSerializer, RoadmapSerializer, StepSerializer, StudentProgressSerializer


def visible_roadmaps(request):
    roadmaps = Roadmap.objects.all()
    role = getattr(request.user, "effective_role", None)

    if role in ["admin", "instructor"]:
        return roadmaps
    return roadmaps.filter(status="published")


class InstructorPageView(TemplateView):
    template_name = "instructor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_steps"] = Step.objects.select_related("roadmap").order_by(
            "roadmap__title", "order"
        )
        return context


class RoadmapListCreateView(generics.ListCreateAPIView):
    serializer_class = RoadmapSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        return visible_roadmaps(self.request).order_by("-created_at")

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required to create a roadmap.")
        serializer.save(created_by=self.request.user)


class RoadmapDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoadmapSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        return visible_roadmaps(self.request).order_by("-created_at")


class StepListCreateView(generics.ListCreateAPIView):
    serializer_class = StepSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        roadmap_id = self.kwargs.get("roadmap_id") or self.request.data.get("roadmap")

        if not roadmap_id:
            raise ValidationError({"roadmap": "This field is required when creating a step."})

        roadmap = Roadmap.objects.get(pk=roadmap_id)

        serializer.save(
            roadmap=roadmap,
            instructor=self.request.user,
        )

    def get_queryset(self):
        roadmap_id = self.kwargs.get("roadmap_id")
        steps = Step.objects.filter(roadmap__in=visible_roadmaps(self.request))

        if roadmap_id is not None:
            return steps.filter(roadmap_id=roadmap_id).order_by("order")

        return steps.order_by("order")


class StepDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StepSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        return Step.objects.all().order_by("order")


class CompleteStepView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        step = get_object_or_404(Step, pk=pk)

        progress, _ = StudentProgress.objects.get_or_create(
            student=request.user,
            step=step,
            defaults={"status": "completed", "completed_at": timezone.now()}
        )
        progress.status = "completed"
        progress.completed_at = timezone.now()
        progress.save(update_fields=["status", "completed_at"])

        # Unlock next step in order
        next_step = Step.objects.filter(
            roadmap=step.roadmap,
            order__gt=step.order
        ).order_by("order").first()

        if next_step:
            StudentProgress.objects.get_or_create(
                student=request.user,
                step=next_step,
                defaults={"status": "active"}
            )

        return Response({
            "status": "completed",
            "step_id": step.id,
            "step_title": step.title,
            "roadmap_id": step.roadmap.id,
            "next_step_id": next_step.id if next_step else None,
            "next_step_title": next_step.title if next_step else None,
            "next_step_order": next_step.order if next_step else None,
        })


class LearningContentListCreateView(generics.ListCreateAPIView):
    serializer_class = LearningContentSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        step_id = self.kwargs.get("step_id")
        if step_id is None:
            return LearningContent.objects.all().order_by("-created_at")

        contents = LearningContent.objects.filter(
            step_id=step_id,
            step__roadmap__in=visible_roadmaps(self.request),
        )
        return contents.order_by("created_at")

    def perform_create(self, serializer):
        step_id = (
            self.kwargs.get("step_id")
            or self.request.data.get("step")
            or self.request.data.get("step_id")
        )

        if not step_id:
            raise ValidationError({"step": "This field is required when creating learning content."})

        try:
            step = Step.objects.get(pk=step_id)
        except Step.DoesNotExist:
            raise ValidationError({"step": "Select an existing step."})

        serializer.save(step=step)


class LearningContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LearningContentSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsInstructorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        return LearningContent.objects.all().order_by("-created_at")


class StudentProgressListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentProgressSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required to create progress.")
        serializer.save(student=self.request.user)

    def get_queryset(self):
        return StudentProgress.objects.filter(
            student=self.request.user
        )


class StudentProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return StudentProgress.objects.filter(
            student=self.request.user
        )
    serializer_class = StudentProgressSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
