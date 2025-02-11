# backend/blog_generator/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet

router = DefaultRouter()
router.register(r'blogs', BlogPostViewSet, basename='blog')

urlpatterns = [
    path('', include(router.urls)),
]