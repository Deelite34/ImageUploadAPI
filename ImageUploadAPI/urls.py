from django.contrib import admin
from django.urls import path, include
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('API.urls')),
    path('', include('img.urls'), name='root'),
    path('__debug__/', include(debug_toolbar.urls)),
]
