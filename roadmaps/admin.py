from django.contrib import admin
from .models import Roadmap, Step, LearningContent, StudentProgress

admin.site.register(Roadmap)
admin.site.register(Step)
admin.site.register(LearningContent)
admin.site.register(StudentProgress)