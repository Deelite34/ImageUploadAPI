from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import ImageUploadView, TimeLimitedThumbnailView

router = DefaultRouter()
router.register('all', ImageUploadView, basename='standard')
router.register('timed', TimeLimitedThumbnailView, basename='timed')


urlpatterns = [
    path('', include(router.urls), name='thumbnail'),
    path('auth/', include('djoser.urls.authtoken')),
]
