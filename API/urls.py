from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import ImageUploadView

router = DefaultRouter()
router.register('thumbnail', ImageUploadView, basename='thumbnail')


urlpatterns = [
    path('hello/', views.HelloWorldView.as_view(), name='hello'),
    path('', include(router.urls), name='thumbnail'),
]