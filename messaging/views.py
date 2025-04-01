from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm

# Home view: If user is logged in, redirect to home, else show login
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
            # If form is invalid, check the errors
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
    Ensures that the user is logged in and passes the room name to the template.
    """
    # Render the chat room template with the room name as context
    return render(request, 'messaging/chat_room.html', {'room_name': room_name})
