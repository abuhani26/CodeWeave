from django.db import models




class Quiz(models.Model):
    title = models.CharField(max_length=255)
    step = models.ForeignKey('roadmaps.Step', on_delete=models.CASCADE, related_name='quizzes')

    def __str__(self):
        return self.title
    

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['order']
        constraints = [models.UniqueConstraint(fields=['quiz', 'order'], name='unique_question_order')]

    def __str__(self):
        return f"Question {self.order}"
    

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


    def __str__(self):
        return self.text
    
    
class QuizAttempt(models.Model):
    student = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)
    attempt_number = models.PositiveSmallIntegerField()
    passed = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'quiz', 'attempt_number'],name='unique_attempt_number')]
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score})"
    
class StudentAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='student_answers')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['attempt', 'question'], name='unique_student_answer')]

    def __str__(self):
        return f"{self.attempt.student.username} - Question {self.question.order}"