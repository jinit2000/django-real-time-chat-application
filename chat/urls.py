from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('room/<int:pk>/', views.room, name='room'),
    path('room/create/', views.create_room, name='create-room'),
    path('room/<int:pk>/edit/', views.edit_room, name='edit-room'),
    path('room/<int:pk>/delete/', views.delete_room, name='delete-room'),
    path('message/<int:pk>/delete/', views.delete_message, name='delete-message'),
    path('topics/', views.topic_list, name='topics'),
    path('profile/<int:pk>/', views.user_profile, name='profile'),
]
