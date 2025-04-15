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
import json

# Home view - redirects to chat if logged in, else to login
def home_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='general')  # Redirect to chat if authenticated
    return render(request, 'messaging/home.html')  # Render home.html for unauthenticated users


def register_view(request):
    if request.user.is_authenticated:
        # Maybe redirect to a dashboard or home page instead of a specific chat room?
        return redirect('home') # Or wherever logged-in users should go

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            raw_password = form.cleaned_data.get('password')
            user.set_password(raw_password)
            user.is_active = True
            user.save()
            login(request, user) # Log the user in
            messages.success(request, 'Registration successful! You are now logged in.')
            # Redirect to a page users should see after registering AND logging in
            return redirect('home') # Or 'chat_room' if that's intended
        else:
            # Form is invalid, add error messages (optional, as errors are usually in form.errors)
            # You can rely on the template to display form.errors
            messages.error(request, 'Please correct the errors below.')
            # The code will now fall through to the render() call below,
            # passing the *invalid* form instance to the template.
    else: # This is a GET request
        form = RegisterForm() # Create an empty form instance

    # Render the template for GET requests OR for invalid POST requests
    # Make sure 'your_app_name/register_template.html' matches the actual path to your template
    context = {'form': form}
    return render(request, 'messaging/register.html', context) # USE YOUR ACTUAL TEMPLATE PATH
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
    print("create_group_chat view called")
    if request.method == 'POST':
        print("Request method is POST")
        try:
            print("Attempting to parse request body")
            body_before_read = request.body  # Try to capture the body before reading
            data = json.loads(request.body.decode('utf-8'))
            print("Request body parsed successfully")
            group_name = data.get('name')
            member_ids = data.get('members', [])

            if not group_name:
                print("Error: Group name is missing")
                return JsonResponse({"error": "Group name is required.", "success": False}, status=400)

            group_chat = Groupchat.objects.create(name=group_name, admin=request.user)
            group_chat.members.add(request.user)  

            for member_id in member_ids:
                try:
                    member = User.objects.get(id=member_id)
                    group_chat.members.add(member)
                except User.DoesNotExist:
                    print(f"Warning: User with ID {member_id} not found.")

            group_chat.save()
            print(f"Group '{group_name}' created successfully with ID: {group_chat.id}")
            return JsonResponse({"success": True, "message": "Group created successfully", "group_id": group_chat.id}, status=201)

        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}, Request body: {body_before_read.decode('utf-8') if 'body_before_read' in locals() else 'Could not read body'}")
            return JsonResponse({"error": "Invalid JSON data in request body.", "success": False}, status=400)
        except Exception as e:
            print(f"Error creating group: {e}")
            return JsonResponse({"error": "Failed to create group.", "success": False}, status=500)

    else:
        print("Request method is not POST")
    return JsonResponse({"error": "Invalid request method", "success": False}, status=405)
   
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

@login_required
def get_groups(request):
    print("get_groups view called")
    try:
        group_chats = Groupchat.objects.filter(members=request.user)
        print(f"Number of groups found for user {request.user.username}: {len(group_chats)}")
        groups_data = [{
            "id": group.id,
            "name": group.name
        } for group in group_chats]
        print(f"Groups data: {groups_data}")
        return JsonResponse({"groups": groups_data})
    except Exception as e:
        print(f"Error in get_groups view: {e}")
        return JsonResponse({"error": str(e)}, status=500)
# views.py
@login_required
def add_member_to_group(request, group_id):
    group_chat = get_object_or_404(Groupchat, id=group_id)
    
    # Check if the user is the group owner (if you have ownership logic)
    if request.user not in group_chat.members.all():
        return JsonResponse({"error": "You are not a member of this group."})
    
    # Get the list of friends
    friends = Friend.objects.filter(user=request.user)
    
    # Handling the friend to add
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')  # ID of the friend to add
        friend = get_object_or_404(User, id=friend_id)
        
        # Ensure the user is actually friends
        if not Friend.objects.filter(user=request.user, friend=friend).exists():
            return JsonResponse({"error": "You can only add your friends to the group."})
        
        # Add the friend to the group chat
        group_chat.members.add(friend)
        
        return JsonResponse({"success": True, "message": f"{friend.username} has been added to the group."})

    return render(request, 'messaging/add_member_to_group.html', {
        'group_chat': group_chat,
        'friends': friends
    })

@login_required
def group_chat_room(request, group_id):
    group_chat = get_object_or_404(Groupchat, id=group_id)
    
    # Ensure user is part of the group chat
    if request.user not in group_chat.members.all():
        return redirect('home')  # Redirect if not a member of the group
    
    messages = Groupmchatmessage.objects.filter(group_chat=group_chat)
    
    return render(request, 'messaging/chat_room.html', {
        'group_chat': group_chat,
        'messages': messages
    })

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



@login_required
def delete_account(request):
    if request.method == 'POST':
        try:
            user = request.user
            user.delete()  # Delete the logged-in user's account
            
            # Clear the session after deletion
            request.session.flush()

            # Show success message after account deletion
            messages.success(request, "Your account has been deleted successfully.")

            # Redirect to home after clearing the session
            return redirect('home')  # Redirect to the home page after deletion
        except Exception as e:
            messages.error(request, f"An error occurred while deleting your account: {str(e)}")
            return redirect('home')  # Redirect to home if an error occurs

    # If the method is GET, you can directly redirect to home without any confirmation.
    return redirect('home')
