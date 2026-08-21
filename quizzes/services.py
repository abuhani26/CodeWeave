from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from roadmaps.models import Step, StudentProgress
from .models import Choice, Question, Quiz, QuizAttempt, StudentAnswer


def submit_quiz(student, quiz_id, answers):
    """
    Evaluate a student's submission for a quiz and persist the attempt result.
    """
    quiz = get_object_or_404(Quiz.objects.select_related("step", "step__roadmap"), pk=quiz_id)

    questions = Question.objects.filter(quiz=quiz).select_related("quiz")
    correct_answers = set(
        Choice.objects.filter(question__quiz=quiz, is_correct=True)
        .values_list("question_id", "id")
    )

    score = Decimal("0")
    question_count = questions.count()

    if question_count == 0:
        return {
            "quiz": quiz.id,
            "quiz_title": quiz.title,
            "step_id": quiz.step.id,
            "step_title": quiz.step.title,
            "step_order": quiz.step.order,
            "roadmap_id": quiz.step.roadmap.id,
            "unlock_score": quiz.step.unlock_score,
            "score": 0.0,
            "passed": False,
            "total_questions": 0,
            "correct_answers": 0,
            "attempt_number": 1,
            "next_step_id": None,
            "next_step_title": None,
            "next_step_order": None,
        }

    next_step = None

    with transaction.atomic():
        last_attempt = (
            QuizAttempt.objects.filter(student=student, quiz=quiz)
            .order_by("-attempt_number")
            .first()
        )
        attempt_number = 1 if last_attempt is None else last_attempt.attempt_number + 1

        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=0,
            attempt_number=attempt_number,
            passed=False,
        )

        for answer in answers:
            question_id = answer["question"]
            choice_id = answer["choice"]

            question = get_object_or_404(Question, pk=question_id, quiz=quiz)
            choice = get_object_or_404(Choice, pk=choice_id, question=question)

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                choice=choice,
            )

            if (question.id, choice.id) in correct_answers:
                score += Decimal("100") / Decimal(question_count)

        score = round(score, 2)
        attempt.score = score
        attempt.passed = score >= Decimal(quiz.step.unlock_score)
        attempt.save(update_fields=["score", "passed"])

        progress, _ = StudentProgress.objects.get_or_create(
            student=student,
            step=quiz.step,
            defaults={"status": "active", "best_score": score},
        )
        progress.best_score = max(progress.best_score or Decimal("0"), score)

        next_step = Step.objects.filter(
            roadmap=quiz.step.roadmap,
            order__gt=quiz.step.order,
        ).order_by("order").first()

        if attempt.passed:
            progress.status = "completed"
            progress.completed_at = timezone.now()
            if next_step:
                StudentProgress.objects.get_or_create(
                    student=student,
                    step=next_step,
                    defaults={"status": "active"},
                )
        elif progress.status == "locked":
            progress.status = "active"

        progress.save(update_fields=["status", "best_score", "completed_at"])

    correct_count = int(round((float(score) / 100.0) * question_count))

    return {
        "quiz": quiz.id,
        "quiz_title": quiz.title,
        "step_id": quiz.step.id,
        "step_title": quiz.step.title,
        "step_order": quiz.step.order,
        "roadmap_id": quiz.step.roadmap.id,
        "unlock_score": quiz.step.unlock_score,
        "score": float(score),
        "passed": attempt.passed,
        "total_questions": question_count,
        "correct_answers": correct_count,
        "attempt_number": attempt_number,
        "next_step_id": next_step.id if next_step else None,
        "next_step_title": next_step.title if next_step else None,
        "next_step_order": next_step.order if next_step else None,
    }
