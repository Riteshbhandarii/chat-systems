#messaging/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse 
from .forms import MessageForm
from .models import Message

# Create your views here.

def send_message(request):
    if request.method == "POST": # checking if the request is POST Request
        form = MessageForm(request.POST) # holds the uses message temporarily to be processed
        if form.is_valid(): # checks if form/users output is valid
            form.save() #saves the message to db
            if request.is_ajax(): # checks if the request is AJAX request 
                return JsonResponse({ 
                    "content": form.cleaned_data["content"],
                    "sender" : form.cleaned_data["sender"].username,
                }) # sends message to other user/users
            return JsonResponse({"error": "Invalid request"}, status= 400) 

def messaging_list(request): 
    messages = Message.objects.all() # retrieves all the Message objects from the database
    return render(request, "messaging_list.html", {"messages": messages}) # desplays the messaage from db to html 

