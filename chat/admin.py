from django.contrib import admin
from .models import Topic, Room, Message

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_count', 'created_at']
    search_fields = ['name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'topic', 'message_count', 'created_at']
    list_filter = ['topic', 'is_private']
    search_fields = ['name', 'host__username']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'body', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'room']
    search_fields = ['user__username', 'body']
