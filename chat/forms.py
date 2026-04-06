from django import forms
from .models import Room, Topic


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'description', 'is_private']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Room name...', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'What is this room about?', 'rows': 3, 'class': 'form-input'}),
        }
