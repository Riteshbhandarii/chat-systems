from django.db import models
from django.contrib.auth.models import User
from django.conf import settings  

class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_of")

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user} ↔ {self.friend}"

class FriendRequest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def accept(self):
        self.status = self.ACCEPTED
        self.save()
        
    def decline(self):
        self.status = self.DECLINED
        self.save()

    def accept(self):
        if self.status == self.PENDING:
            Friend.objects.get_or_create(user=self.sender, friend=self.receiver)
            Friend.objects.get_or_create(user=self.receiver, friend=self.sender)
            self.status = self.ACCEPTED
            self.save()

    def decline(self):
        if self.status == self.PENDING:
            self.status = self.DECLINED
            self.save()

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"

class Groupchat(models.Model):
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(User, related_name="group_chat")

    def __str__(self):
        return self.name

class Groupmchatmessage(models.Model):  # Original spelling preserved
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    group_chat = models.ForeignKey(Groupchat, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name="read_group_messages", blank=True)

    def __str__(self):
        return f"Message in {self.group_chat.name} by {self.sender.username}: {self.content}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        if self.receiver:
            return f"{self.sender.username} to {self.receiver.username}: {self.content}"
        return f"{self.sender.username} (no receiver): {self.content}"