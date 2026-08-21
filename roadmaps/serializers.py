from rest_framework import serializers

from .models import LearningContent, Roadmap, Step, StudentProgress


class LearningContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningContent
        fields = ["id", "title", "description", "content_type", "content", "video_file", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        content = (attrs.get("content") or "").strip()
        video_file = attrs.get("video_file")
        content_type = attrs.get("content_type")

        if not content and not video_file:
            raise serializers.ValidationError({
                "content": "Provide content or upload a video file."
            })

        if video_file:
            if content_type != "video":
                raise serializers.ValidationError({
                    "video_file": "Video files can only be attached to Video content."
                })
            if video_file.size > 100 * 1024 * 1024:
                raise serializers.ValidationError({
                    "video_file": "Video files must be 100 MB or smaller."
                })
            if not (video_file.content_type or "").startswith("video/"):
                raise serializers.ValidationError({
                    "video_file": "Upload a valid video file."
                })

        return attrs


class StepSerializer(serializers.ModelSerializer):
    learning_contents = LearningContentSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Step
        fields = ["id", "title", "order", "difficulty", "unlock_score", "learning_contents", "instructor"]
        read_only_fields = ["id", "instructor"]


class RoadmapSerializer(serializers.ModelSerializer):
    steps = StepSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Roadmap
        fields = ["id", "title", "description", "status", "created_by", "created_at", "updated_at", "steps"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class StudentProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProgress
        fields = ["id", "student", "step", "status", "completed_at", "best_score"]
        read_only_fields = ["id", "student"]
