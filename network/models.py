from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.db.models.signals import post_save


class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)
    def __str__(self):
        return self.user.username

def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()

post_save.connect(create_profile, sender=User)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user")
    content = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content


class PostForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'placeholder': 'What\'s on your mind?', 'style': 'width: 800px; padding:10px; border-radius:10px;', 'autofocus' : True}))
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like")
    post  = models.ForeignKey(Post, on_delete=models.CASCADE ,related_name="post_like")

    def __str__(self):
        return f"{self.user} liked {self.post}"