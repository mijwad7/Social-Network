
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("profile/<int:id>", views.view_profile, name="view_profile"),
    path("follow/<int:id>", views.follow, name="follow"),
    path("following/<int:id>", views.view_following, name="following"),
    path("edit_post", views.edit_post, name="edit_post"),
    path("add_like/<int:post_id>", views.add_like, name="add_like"),
    path("remove_like/<int:post_id>", views.remove_like, name="remove_like")
]
