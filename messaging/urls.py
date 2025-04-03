from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    
    # Friend-related URLs
    path('fetch_contacts/', views.fetch_contacts, name='fetch_contacts'),
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline_friend_request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    
    # Only keep the pending_friend_requests URL
    path('pending_friend_requests/', views.pending_friend_requests, name='pending_friend_requests'),

    path('get_friends/', views.get_friends, name='get_friends'),
]