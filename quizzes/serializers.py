from rest_framework import serializers

from roadmaps.models import Step

from .models import Choice, Question, Quiz, QuizAttempt, StudentAnswer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]
        read_only_fields = ["id"]

class QuestionSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ["id", "quiz", "text", "order", "choices"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        choices_data = validated_data.pop("choices", [])
        question = Question.objects.create(**validated_data)

        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)

        return question


class QuizSerializer(serializers.ModelSerializer):
    step = serializers.PrimaryKeyRelatedField(queryset=Step.objects.all())
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "step", "questions"]
        read_only_fields = ["id"]

class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ["id", "student", "quiz", "score", "completed_at", "attempt_number", "passed"]
        read_only_fields = ["id", "student", "completed_at", "score", "passed", "attempt_number",]


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ["id", "attempt", "question", "choice" ]
        read_only_fields = ["id", "attempt"]


class AnswerSubmissionSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    choice = serializers.IntegerField()

class SubmitQuizSerializer(serializers.Serializer):
    answers = AnswerSubmissionSerializer(many=True)