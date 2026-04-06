from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import RegisterForm, ProfileForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, f'Welcome to Django Real-Time Chat Application, {user.username}!')
            return redirect('home')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Update user email/name
            request.user.email = request.POST.get('email', request.user.email)
            first = request.POST.get('first_name', '').strip()
            last = request.POST.get('last_name', '').strip()
            if first:
                request.user.first_name = first
            if last:
                request.user.last_name = last
            request.user.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', pk=request.user.pk)

    return render(request, 'accounts/edit_profile.html', {'form': form})
