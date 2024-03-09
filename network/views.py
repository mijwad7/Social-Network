from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse
from .models import User, PostForm, Post, Profile, Like
from django.db.models import Count

def index(request):
    posts = Post.objects.annotate(like_count=Count('post_like')).order_by('-timestamp')
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_likes = Like.objects.all()

    liked_posts = []

    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                liked_posts.append(like.post.id)
    except:
        liked_posts = []

    return render(request, "network/index.html", {
        'page_obj': page_obj,
        'liked_posts': liked_posts,
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    

def create(request):
    if request.method=="POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post(
                content=form.cleaned_data['content'],
                author=request.user,
            )
            post.save()
            return HttpResponseRedirect(reverse("index"))

    else:
        form = PostForm()

    return render(request, 'network/create.html', {'form': form})

def view_profile(request, id):
    author = User.objects.get(pk=id)
    profile = Profile.objects.get(pk=id)
    posts = Post.objects.filter(author__id=id).order_by('-timestamp')
    user_profile = None
    
    if request.user.is_authenticated:
        current_user = request.user
        user_profile = Profile.objects.get(user=current_user)
    
    return render(request, 'network/profile.html', {
        'profile' : profile,
        'posts' : posts, 
        'author': author,
        'user_profile': user_profile
    })

def follow(request, id):
    author = User.objects.get(pk=id)
    profile = Profile.objects.get(pk=id)
    posts = Post.objects.filter(author__id=id).order_by('-timestamp')
    current_user = request.user
    user_profile = Profile.objects.get(user=current_user)
    follow_user = profile
    if current_user != follow_user.user:
        if request.method == "POST":
            if follow_user not in user_profile.follows.all():
                user_profile.follows.add(follow_user)
                return HttpResponseRedirect(reverse("view_profile", args=[id]))
            else:
                user_profile.follows.remove(follow_user)
                return HttpResponseRedirect(reverse("view_profile", args=[id]))
    else:
        return render(request,'network/profile.html',{
            'profile' : profile,
            'posts' : posts,
            'user': current_user,
            'user_profile': user_profile,
            'author': author,
            })
    
@login_required
def view_following(request, id):
    current_user = request.user
    user_profile = Profile.objects.get(user=current_user)
    following_profiles = user_profile.follows.all()

    following_users = [profile.user for profile in following_profiles]

    following_posts = Post.objects.filter(author__in=following_users).annotate(like_count=Count('post_like')).order_by('-timestamp')

    paginator = Paginator(following_posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_likes = Like.objects.all()

    liked_posts = []

    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                liked_posts.append(like.post.id)
    except:
        liked_posts = []

    return render(request, 'network/following.html', {
        'following': following_profiles,
        'page_obj': page_obj,
        'liked_posts': liked_posts,
    })




def edit_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        edited_content = request.POST.get('edited_content')
        
        post = Post.objects.get(pk=post_id)
        
        if post.author == request.user:
            post.content = edited_content
            post.save()
            
            return JsonResponse({'new_content': post.content})
    
    return JsonResponse({'error': 'Invalid request'})


def remove_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)

    like = Like.objects.filter(user=user, post=post)
    like.delete()
    return JsonResponse({"message": "Like added successfully"})

def add_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)

    new_like = Like(user=user, post=post)
    new_like.save()
    return JsonResponse({"message": "Like added successfully"})