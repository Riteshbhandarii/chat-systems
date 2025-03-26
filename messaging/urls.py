from django.urls import path
from messaging.views import login_view, register_view, logout_view

urlpatterns = [
    path('', login_view, name='root'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'), 
    path('logout/', logout_view, name='logout'),
]