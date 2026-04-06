from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def room_count(self):
        return self.rooms.count()


class Room(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='rooms')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    participants = models.ManyToManyField(User, related_name='joined_rooms', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    @property
    def message_count(self):
        return self.messages.count()

    @property
    def participant_count(self):
        return self.participants.count()


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username}: {self.body[:50]}'
