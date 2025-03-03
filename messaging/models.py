from django.db import models
from django.contrib.auth.models import User

# represents the group
# Group chat model which handels the group chats and their members
class Groupchat(models.Model):
    name = models.CharField(max_length= 255, unique= True) # creates a field for stroping groupchat name
    members = models.ManyToManyField(User, related_name = "group_chat") # links users to the group chat, so chat can have many users. 
    
    def __str__(self):
        return self.name
    
    # represents indivudual messages sent within a group chat
class Groupmchatmessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)  # connects each message to user
    group_chat = models.ForeignKey(Groupchat, on_delete=models.CASCADE) # connects each message to group chat
    content = models.TextField() 
    timestamp = models.DateTimeField(auto_now_add = True) # Time when the message was created
    read_by = models.ManyToManyField(User, related_name="read_group_messages", blank=True)

    def __str__(self):
        return f"Message in {self.group_chat.name} by {self.sender.username}: {self.content}"
  

class Message(models.Model): #Data base for the messages 1 on 1 ( sender and reciver)
    sender = models.ForeignKey(User, on_delete=models.CASCADE) # links each messages to a user
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, null =True, blank = True)  # User who receives the message
    content = models.TextField() #storing the message text
    timestamp = models.DateTimeField(auto_now_add=True) # records the time, does not change when the message is updated. 
    read = models.BooleanField(default =False) # checks if the message is read or not
    
    # makes the message and username readable when printed or viewed in django
    def __str__(self):
       return f"{self.sender.username} to {self.receiver.username}: {self.content}"

