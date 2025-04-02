from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import FriendRequest, Friend, Groupchat, Groupmchatmessage


# Home view: If user is logged in, redirect to chat room, else show login
def home_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')  # Redirect to the chat room if logged in
    return render(request, 'messaging/home.html')

# Register view: If logged in, redirect to home page, else show registration form
def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')  # Redirect to chat room if already logged in

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()

            # Log the user in automatically
            login(request, user)

            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('chat_room', room_name='general')  # Redirect to chat room after registration
        else:
            messages.error(request, "There are errors in the form. Please check the fields.")
            return render(request, 'messaging/register.html', {'form': form})

    else:
        form = RegisterForm()

    return render(request, 'messaging/register.html', {'form': form})

# Login view: If logged in, redirect to chat room, else handle login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')  # Redirect to chat room if already logged in

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return render(request, "messaging/login.html", {"error": "Username and password are required."})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat_room', room_name='general')  # Redirect to chat room after successful login
        else:
            return render(request, "messaging/login.html", {"error": "Invalid credentials"})

    return render(request, "messaging/login.html")

# Logout view: Log out the user and redirect to login page
def logout_view(request):
    logout(request)  # Logs the user out
    return redirect('login')  # Redirect to login page after logout

# Chat room view: Render the chat room page (ensure user is logged in)
@login_required
def chat_room(request, room_name):
    """
    View to render the chat room page.
    Ensures that the user is logged in and passes the room name as context.
    """
    # Render the chat room template with the room name as context
    return render(request, 'messaging/chat_room.html', {'room_name': room_name})

# Send a friend request
@login_required
def send_friend_request(request, username):
    receiver = get_object_or_404(User, username=username)
    if receiver == request.user:
        return JsonResponse({"error": "You cannot send a friend request to yourself."})

    # Check if a request already exists
    if FriendRequest.objects.filter(sender=request.user, receiver=receiver, status='pending').exists():
        return JsonResponse({"error": "Friend request already sent."})

    # Create a new friend request
    friend_request = FriendRequest(sender=request.user, receiver=receiver)
    friend_request.save()

    return JsonResponse({"message": f"Friend request sent to {receiver.username}."})

# Search users to send a friend request
@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    return render(request, 'messaging/search_results.html', {'users': users, 'query': query})

# Accept a friend request
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    friend_request.accept()
    return JsonResponse({"message": "Friend request accepted"})

# Decline a friend request
@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    friend_request.decline()
    return JsonResponse({"message": "Friend request declined"})

# View friend list
@login_required
def view_friends(request):
    friends = Friend.objects.filter(user=request.user)
    return render(request, 'messaging/friend_list.html', {'friends': friends})

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
    
    return render(request, 'messaging/create_group_chat.html')

# Send message to a group chat
@login_required
def send_group_message(request, group_id):
    group_chat = get_object_or_404(Groupchat, id=group_id)
    if request.user not in group_chat.members.all():
        return JsonResponse({"error": "You are not a member of this group."})

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if not message_content:
            return JsonResponse({"error": "Message content cannot be empty."})

        group_message = Groupmchatmessage(sender=request.user, group_chat=group_chat, content=message_content)
        group_message.save()

        return JsonResponse({"message": "Message sent."})

    return render(request, 'messaging/send_group_message.html', {'group_chat': group_chat})

