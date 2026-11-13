"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from roadmaps.views import InstructorPageView
from .views import serve_media_with_range

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='accounts/login.html'), name='login-page'),
    path('register/', TemplateView.as_view(template_name='accounts/register.html'), name='register-page'),
    path('profile/', TemplateView.as_view(template_name='accounts/profile.html'), name='profile-page'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard-page'),
    path('instructor/', InstructorPageView.as_view(), name='instructor-page'),
    path('roadmaps/', TemplateView.as_view(template_name='roadmaps/list.html'), name='roadmaps-page'),
    path('roadmaps/<int:roadmap_id>/', TemplateView.as_view(template_name='roadmaps/detail.html'), name='roadmap-detail-page'),
    path('quizzes/<int:quiz_id>/', TemplateView.as_view(template_name='quizzes/detail.html'), name='quiz-detail-page'),
    path("api/accounts/", include("accounts.urls")),
    path("api/roadmaps/", include("roadmaps.urls")),
    path("api/quizzes/", include("quizzes.urls")),
    re_path(r'^media/(?P<path>.*)$', serve_media_with_range, name='serve-media-range'),
]
