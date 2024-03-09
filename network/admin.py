from django.contrib import admin
from .models import Post, Profile, User, Like
# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Like)



