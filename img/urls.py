from django.conf.urls.static import static
from django.urls import path
from ImageUploadAPI import settings
from img.views import DisplayImageView

urlpatterns = [
    path('i/<str:slug>/', DisplayImageView.as_view(), name="display_image"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
