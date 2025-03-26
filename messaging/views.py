from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm

def register_view(request):
    # Only redirect if user is authenticated AND trying to access register page
    if request.user.is_authenticated and request.path == '/register/':
        return render(request, 'messaging/register.html', {'form': RegisterForm()})
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'messaging/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        # Show the login page but with a "you're already logged in" message
        return render(request, "messaging/login.html", {"message": "You are already logged in"})
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return render(request, "messaging/login.html", {"error": "Username and password are required."})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # After login, show register page but don't redirect
            return render(request, 'messaging/register.html', {'form': RegisterForm()})
        else:
            return render(request, "messaging/login.html", {"error": "Invalid credentials"})

    return render(request, "messaging/login.html")

def logout_view(request):
    logout(request)
    return redirect('login')