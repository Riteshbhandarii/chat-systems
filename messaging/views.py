from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import FriendRequest, Friend, Groupchat, Groupmchatmessage
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone

# Home view - redirects to chat if logged in, else to login
def home_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')  # Redirect to chat if authenticated
    return render(request, 'messaging/home.html')  # Render home.html for unauthenticated users

# Registration view
def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create user object but don’t save to DB yet
            user = form.save(commit=False)

            # Hash the password
            raw_password = form.cleaned_data.get('password')
            user.set_password(raw_password)

            user.is_active = True  # just to be safe
            user.save()

            # Log the user in after registration
            login(request, user)

            messages.success(request, 'Registration successful!')
            return redirect('chat_room', room_name='general')
        
        # Show form errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()

    return render(request, 'messaging/register.html', {'form': form})

# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chat_room', room_name='general')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "messaging/login.html", {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')

# Chat room view
@login_required
def chat_room(request, room_name):
    friend_requests = FriendRequest.objects.filter(receiver=request.user, status='pending').select_related('sender')
    friends = Friend.objects.filter(user=request.user)
    
    return render(request, 'messaging/chat_room.html', {
        'room_name': room_name,
        'friend_requests': friend_requests,
        'friends': friends
    })

# Friend request handling
@csrf_exempt
@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    
    if receiver == request.user:
        return JsonResponse({"error": "You cannot send a friend request to yourself."})

    if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
        return JsonResponse({"error": "Friend request already exists."})

    friend_request = FriendRequest.objects.create(
        sender=request.user,
        receiver=receiver,
        status='pending'
    )
    
    return JsonResponse({
        "message": f"Friend request sent to {receiver.username}.",
        "sender_username": request.user.username,
        "request_id" : friend_request.id
    })

# Decline friend request
@login_required
def decline_friend_request(request, request_id):
    try:
        # Fetch the FriendRequest object by its ID
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)

        # Ensure that the request is still pending
        if friend_request.status != 'pending':
            return JsonResponse({"error": "This friend request has already been processed."})

        # Mark the request as declined
        friend_request.status = 'declined'
        friend_request.save()

        return JsonResponse({"success": True, "message": "Friend request declined."})

    except Exception as e:
        return JsonResponse({"error": f"Failed to decline friend request: {str(e)}"})
# User search
@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id) if query else User.objects.none()
    
    users_data = [{'id': user.id, 'username': user.username} for user in users]
    return JsonResponse({'users': users_data})

# Friend request management

@login_required
def accept_friend_request(request, request_id):
    try:
        # Fetch the FriendRequest object by its ID
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)

        # Ensure that the request is still pending
        if friend_request.status != 'pending':
            return JsonResponse({"error": "This friend request has already been processed."})

        # Mark the request as accepted
        friend_request.status = 'accepted'
        friend_request.save()

        # Create the friendship between the receiver and sender if not exists
        if not Friend.objects.filter(user=request.user, friend=friend_request.sender).exists():
            Friend.objects.create(
                user=request.user, 
                friend=friend_request.sender,
                created_at=timezone.now()  # Manually set the created_at field
            )

        if not Friend.objects.filter(user=friend_request.sender, friend=request.user).exists():
            Friend.objects.create(
                user=friend_request.sender, 
                friend=request.user,
                created_at=timezone.now()  # Manually set the created_at field
            )

        return JsonResponse({"success": True, "message": "Friend request accepted."})

    except Exception as e:
        return JsonResponse({"error": f"Failed to accept friend request: {str(e)}"})

# Contacts and friends
@login_required
def fetch_contacts(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    users_data = [{'id': user.id, 'username': user.username} for user in users]
    return JsonResponse({'users': users_data})

@login_required
def view_friends(request):
    friends = Friend.objects.filter(user=request.user)
    return render(request, 'messaging/chat_room.html', {'friends': friends})

# Group chat functionality
@login_required
def create_group_chat(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if not group_name:
            return JsonResponse({"error": "Group name is required."})

        group_chat = Groupchat.objects.create(name=group_name)
        group_chat.members.add(request.user)
        group_chat.save()

        return redirect('chat_room', room_name=group_chat.name)

    return render(request, 'messaging/chat_room.html')

@login_required
def send_group_message(request, group_id):
    group_chat = get_object_or_404(Groupchat, id=group_id)

    if request.user not in group_chat.members.all():
        return JsonResponse({"error": "You are not a member of this group."})

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if not message_content:
            return JsonResponse({"error": "Message content cannot be empty."})

        group_message = Groupmchatmessage.objects.create(
            sender=request.user, 
            group_chat=group_chat, 
            content=message_content
        )

        return JsonResponse({"message": "Message sent."})

    return render(request, 'messaging/chat_room.html', {'group_chat': group_chat})

# Friend requests management
@login_required
def pending_friend_requests(request):
    requests = FriendRequest.objects.filter(
        receiver=request.user,
        status='pending'
    ).select_related('sender')
    
    requests_data = [{
        'id': req.id,
        'sender_id': req.sender.id,
        'sender_username': req.sender.username,
        'timestamp': req.timestamp.strftime("%Y-%m-%d %H:%M")
    } for req in requests]
    
    return JsonResponse({'requests': requests_data})

@login_required
def get_friends(request):
    friends = Friend.objects.filter(user=request.user)
    friends_data = [{
        "id": friend.friend.id, 
        "username": friend.friend.username
    } for friend in friends]
    return JsonResponse({"friends": friends_data})
