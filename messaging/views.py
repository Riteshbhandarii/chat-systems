from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import FriendRequest, Friend, Groupchat, Groupmchatmessage 
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_exempt

# Home view: Redirect to chat room if logged in, else show login page
def home_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')
    return render(request, 'messaging/chat_room.html')

# Register view: Show registration form and handle registration logic
def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('chat_room', room_name='general')

        messages.error(request, "There are errors in the form. Please check the fields.")
        return render(request, 'messaging/chat_room.html', {'form': form})

    form = RegisterForm()
    return render(request, 'messaging/chat_room.html', {'form': form})

# Login view: Handle user login logic
def login_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "messaging/login.html")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('chat_room', room_name='general')

        messages.error(request, "Invalid credentials")
        return render(request, "messaging/login.html")

    # Add this line to handle GET requests
    return render(request, "messaging/login.html")

# Logout view: Logs out the user and redirects to login page
# Added CSRF exemption as a possible fix

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have successfully logged out.")
    return redirect('login')  # Moved outside the if block
 #chat at room view: Render the chat room page if user is logged in
@login_required
def chat_room(request, room_name):
    # Get pending friend requests
    friend_requests = FriendRequest.objects.filter(receiver=request.user, status='pending').select_related('sender')

    # Fetch friends of the user
    friends = Friend.objects.filter(user=request.user)
    
    return render(request, 'messaging/chat_room.html', {
        'room_name': room_name,
        'friend_requests': friend_requests,
        'friends': friends
    })

# Send a friend request
@csrf_exempt
@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    
    if receiver == request.user:
        return JsonResponse({"error": "You cannot send a friend request to yourself."})

    # Check if any request exists (pending, accepted or declined)
    if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
        return JsonResponse({"error": "Friend request already exists."})

    # Create new request
    friend_request = FriendRequest.objects.create(
        sender=request.user,
        receiver=receiver,
        status='pending'
    )
    
    return JsonResponse({
        "message": f"Friend request sent to {receiver.username}.",
        "sender_username": request.user.username  # Ensure this is included
    })
# Search users to send a friend request
@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id) if query else User.objects.none()
    
    users_data = [{'id': user.id, 'username': user.username} for user in users]
    return JsonResponse({'users': users_data})

# Accept a friend request
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    friend_request.status = 'accepted'
    friend_request.save()

    # Add to friend list
    Friend.objects.get_or_create(user=request.user, friend=friend_request.sender)
    Friend.objects.get_or_create(user=friend_request.sender, friend=request.user)

    return JsonResponse({"message": "Friend request accepted"})

# Decline a friend request
@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    friend_request.status = 'declined'
    friend_request.save()
    return JsonResponse({"message": "Friend request declined"})

# Fetch contacts (usernames only)
@login_required
def fetch_contacts(request):
    query = request.GET.get('q', '').strip()
    
    # Only search if query has at least 2 characters
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    
    users_data = [{'id': user.id, 'username': user.username} for user in users]
    return JsonResponse({'users': users_data})

# View friend list
@login_required
def view_friends(request):
    friends = Friend.objects.filter(user=request.user)
    return render(request, 'messaging/chat_room.html', {'friends': friends})

# Create a new group chat
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

# Send a message to a group chat
@login_required
def send_group_message(request, group_id):
    group_chat = get_object_or_404(Groupchat, id=group_id)

    if request.user not in group_chat.members.all():
        return JsonResponse({"error": "You are not a member of this group."})

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if not message_content:
            return JsonResponse({"error": "Message content cannot be empty."})

        group_message = GroupchatMessage(sender=request.user, group_chat=group_chat, content=message_content)
        group_message.save()

        return JsonResponse({"message": "Message sent."})

    return render(request, 'messaging/chat_room.html', {'group_chat': group_chat})

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
    # Fetch the friends of the logged-in user
    friends = Friend.objects.filter(user=request.user)

    # Prepare a response containing the friends list
    friends_data = [{"id": friend.friend.id, "username": friend.friend.username} for friend in friends]
    return JsonResponse({"friends": friends_data})
