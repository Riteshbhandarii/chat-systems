from django.urls import path
from .views import login_view, chat_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('chat/', chat_view, name='chat'),
]
