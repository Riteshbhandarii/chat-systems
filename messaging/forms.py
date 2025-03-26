# messaging/forms.py 

from django import forms # imports forms module from django
from .models import Message #imports Message model from models.py


class MessageForm(forms.ModelForm): # creates form based on models fields. 
    class Meta: # configuration for the form
        model = Message # form is associated with the Message
        fields = ["sender", "receiver", "content"] # users options
        
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
