from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import LearningContent, Roadmap, Step


class RoadmapLogicTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="StrongPass123!",
            role="instructor",
        )
        self.roadmap = Roadmap.objects.create(
            title="Roadmap One",
            description="Test roadmap",
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

    def test_step_list_route_without_roadmap_id_returns_200(self):
        response = self.client.get(reverse("step-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_nested_step_list_route_returns_only_steps_for_roadmap(self):
        response = self.client.get(
            reverse("roadmap-step-list", kwargs={"roadmap_id": self.roadmap.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["title"], "Step One")

    def test_learning_content_can_be_attached_to_existing_step_via_api(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("learning-content-list-create"),
            {
                "step": self.step.pk,
                "title": "Lesson notes",
                "description": "A useful summary",
                "content_type": "article",
                "content": "Read this carefully.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LearningContent.objects.count(), 1)
        self.assertEqual(LearningContent.objects.get().step, self.step)

    def test_learning_content_can_be_attached_using_step_id_alias(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("learning-content-list-create"),
            {
                "step_id": self.step.pk,
                "title": "Alias content",
                "description": "A fallback payload",
                "content_type": "link",
                "content": "https://example.com/lesson",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LearningContent.objects.count(), 1)
        self.assertEqual(LearningContent.objects.get().step, self.step)

    def test_instructor_can_upload_a_video_file_for_a_step(self):
        self.client.force_authenticate(user=self.user)
        video = SimpleUploadedFile(
            "lesson.mp4",
            b"video-file-content",
            content_type="video/mp4",
        )

        response = self.client.post(
            reverse("learning-content-list-create"),
            {
                "step": self.step.pk,
                "title": "Video lesson",
                "description": "An uploaded lesson",
                "content_type": "video",
                "video_file": video,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        learning_content = LearningContent.objects.get()
        self.assertEqual(learning_content.step, self.step)
        self.assertTrue(learning_content.video_file.name.endswith("lesson.mp4"))
        learning_content.video_file.delete(save=False)

    def test_student_can_only_view_published_roadmaps_and_their_steps(self):
        draft_roadmap = Roadmap.objects.create(
            title="Draft roadmap",
            description="Not ready for students",
            created_by=self.user,
            status="draft",
        )
        Step.objects.create(
            roadmap=draft_roadmap,
            instructor=self.user,
            title="Draft step",
            order=1,
        )
        student = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.client.force_authenticate(user=student)

        list_response = self.client.get(reverse("roadmap-list"))
        step_response = self.client.get(reverse("step-list-create"))
        draft_response = self.client.get(
            reverse("roadmap-detail", kwargs={"pk": draft_roadmap.pk})
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in list_response.json()], [self.roadmap.pk])
        self.assertEqual([item["id"] for item in step_response.json()], [self.step.pk])
        self.assertEqual(draft_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_instructor_can_view_their_own_draft_roadmaps_only(self):
        own_draft = Roadmap.objects.create(
            title="My draft roadmap",
            description="Still being prepared",
            created_by=self.user,
            status="draft",
        )
        other_instructor = get_user_model().objects.create_user(
            username="another-instructor",
            email="another-instructor@example.com",
            password="StrongPass123!",
            role="instructor",
        )
        Roadmap.objects.create(
            title="Another instructor roadmap",
            description="Not owned by the current instructor",
            created_by=other_instructor,
            status="published",
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("roadmap-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["id"] for item in response.json()},
            {self.roadmap.pk, own_draft.pk},
        )
