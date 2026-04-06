from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password', 'class': 'form-input'})


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar_url']
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself...', 'rows': 3, 'class': 'form-input'}),
            'avatar_url': forms.URLInput(attrs={'placeholder': 'Avatar image URL (optional)', 'class': 'form-input'}),
        }
