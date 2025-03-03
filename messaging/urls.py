from django.urls import path
from .views import send_message, messaging_list

urlpatterns = [
    path("send/", send_message, name="send_message"), # sending messages
    path("", messaging_list, name="messaging_list"), # viewing messages
]
