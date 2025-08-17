"""URL configuration for chat_project."""

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('messaging.urls')),  # Include messaging URLs at the root
]

