from django.db import models

class Roadmap(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='roadmaps')
    status = models.CharField(max_length=50, choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Step(models.Model):
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='steps')
    instructor = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    difficulty = models.CharField(max_length=50, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner')
    unlock_score = models.PositiveSmallIntegerField(default=80)

    class Meta:
        ordering = ['order']
        constraints = [models.UniqueConstraint(fields=['roadmap', 'order'], name='unique_step_order')]

    def __str__(self):
        return f"{self.roadmap.title} - Step {self.order}: {self.title}"
    


class LearningContent(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='learning_contents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    content_type = models.CharField(max_length=50, choices=[('video', 'Video'), ('article', 'Article'), ('code', 'Code'),('pdf', 'PDF'),('link', 'Link')], default='link')
    content = models.TextField(blank=True, default="")
    video_file = models.FileField(upload_to="learning_videos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class StudentProgress(models.Model):
    student = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='progress')
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='student_progress')
    status = models.CharField(max_length=20, choices=[('locked','Locked'), ('active','Active'), ('completed','Completed'),], default='locked')
    completed_at = models.DateTimeField(blank=True, null=True)
    best_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'step'], name='unique_student_progress')]

    def __str__(self):
        return f"{self.student.username} - {self.step.title} ({self.status})"
