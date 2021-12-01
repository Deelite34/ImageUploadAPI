from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter


from .views import ImageUploadView, TimeLimitedThumbnailView

router = DefaultRouter()
router.register('all', ImageUploadView, basename='standard')
router.register('timed', TimeLimitedThumbnailView, basename='timed')


urlpatterns = [
    path('', include(router.urls), name='thumbnail'),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
