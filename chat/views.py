from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Room, Topic, Message
from .forms import RoomForm


def home(request):
    q = request.GET.get('q', '')
    topic_filter = request.GET.get('topic', '')

    rooms = Room.objects.select_related('host', 'topic').prefetch_related('participants')

    if q:
        rooms = rooms.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(topic__name__icontains=q) |
            Q(host__username__icontains=q)
        )

    if topic_filter:
        rooms = rooms.filter(topic__name__iexact=topic_filter)

    topics = Topic.objects.annotate(count=Count('rooms')).order_by('-count')[:10]
    recent_messages = Message.objects.select_related('user', 'room').filter(
        is_deleted=False
    ).order_by('-created_at')[:10]

    context = {
        'rooms': rooms,
        'topics': topics,
        'recent_messages': recent_messages,
        'room_count': rooms.count(),
        'q': q,
        'topic_filter': topic_filter,
    }
    return render(request, 'chat/home.html', context)


@login_required
def room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    chat_messages = room.messages.filter(is_deleted=False).select_related('user').order_by('created_at')
    participants = room.participants.all()

    context = {
    'room': room,
    'chat_messages': chat_messages,
    'participants': participants,
    'is_host': request.user == room.host,
}
    return render(request, 'chat/room.html', context)


@login_required
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic', '').strip()
        topic = None
        if topic_name:
            topic, _ = Topic.objects.get_or_create(name=topic_name)

        form = RoomForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.host = request.user
            r.topic = topic
            r.save()
            messages.success(request, f'Room "{r.name}" created!')
            return redirect('room', pk=r.pk)

    return render(request, 'chat/room_form.html', {'form': form, 'topics': topics, 'action': 'Create'})


@login_required
def edit_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.user != room.host:
        messages.error(request, 'Only the host can edit this room.')
        return redirect('room', pk=pk)

    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic', '').strip()
        topic = None
        if topic_name:
            topic, _ = Topic.objects.get_or_create(name=topic_name)

        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            r = form.save(commit=False)
            r.topic = topic
            r.save()
            messages.success(request, 'Room updated!')
            return redirect('room', pk=r.pk)

    return render(request, 'chat/room_form.html', {'form': form, 'topics': topics, 'room': room, 'action': 'Edit'})


@login_required
def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.user != room.host:
        messages.error(request, 'Only the host can delete this room.')
        return redirect('room', pk=pk)

    if request.method == 'POST':
        room_name = room.name
        room.delete()
        messages.success(request, f'Room "{room_name}" deleted.')
        return redirect('home')

    return render(request, 'chat/confirm_delete.html', {'obj': room, 'type': 'room'})


@login_required
@require_POST
def delete_message(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.user == message.user or request.user == message.room.host:
        message.is_deleted = True
        message.body = '[deleted]'
        message.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)


def topic_list(request):
    topics = Topic.objects.annotate(count=Count('rooms')).order_by('-count')
    return render(request, 'chat/topics.html', {'topics': topics})


def user_profile(request, pk):
    from django.contrib.auth.models import User
    profile_user = get_object_or_404(User, pk=pk)
    rooms = profile_user.hosted_rooms.all()
    recent_messages = profile_user.messages.filter(is_deleted=False).order_by('-created_at')[:10]
    topics = Topic.objects.filter(rooms__host=profile_user).distinct()
    context = {
        'profile_user': profile_user,
        'rooms': rooms,
        'recent_messages': recent_messages,
        'topics': topics,
    }
    return render(request, 'chat/profile.html', context)
