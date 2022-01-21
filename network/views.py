import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from datetime import datetime
from .models import *


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

    return render(request, "network/register.html")


def index(request):
    posts = Post.objects.all().order_by('-timestamp')

    paginator = Paginator(posts, 10)

    page_num = request.GET.get('page')
    if page_num is not None:
        try:
            posts = paginator.page(page_num)
        except:
            return HttpResponseRedirect(reverse('index'))

    else:
        posts = paginator.page(1)

    return render(request, "network/index.html", {
        'posts': posts,
        'page_obj': paginator.get_page(page_num)
    })


def profile(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(user=user).order_by('-timestamp')

    paginator = Paginator(posts, 10)

    page_num = request.GET.get('page')
    if page_num is not None:
        try:
            posts = paginator.page(page_num)
        except:
            return HttpResponseRedirect(reverse('profile', args=[username]))

    else:
        posts = paginator.page(1)

    return render(request, 'network/profile.html', {
        'posts': posts,
        'user': user,
        'page_obj': paginator.get_page(page_num)
    })


def following(request):
    posts = []

    for post in Post.objects.all().order_by('-timestamp'):
        if post.user in request.user.following.all():
            posts.append(post)

    paginator = Paginator(posts, 10)

    page_num = request.GET.get('page')
    if page_num is not None:
        try:
            posts = paginator.page(page_num)
        except:
            return HttpResponseRedirect(reverse('following'))

    else:
        posts = paginator.page(1)

    return render(request, 'network/following.html', {
        'posts': posts,
        'page_obj': paginator.get_page(page_num)
    })


@csrf_exempt
@login_required(redirect_field_name='login')
def follow(request, username):

    current_user = request.user
    target_user = User.objects.get(username=username)

    if current_user == target_user:
        return JsonResponse({'error': 'You cannot follow yourself!'}, status=400)

    # If target user is already followed
    elif target_user in current_user.following.all():

        # Unfollow then save both users
        target_user.followers.remove(current_user)
        current_user.following.remove(target_user)

        target_user.save()
        current_user.save()

        return JsonResponse({
            'status': 201,
            'message': 'Unfollowed successfully.'
        }, status=201)

    # Else follow then save
    else:
        target_user.followers.add(current_user)
        current_user.following.add(target_user)

        target_user.save()
        current_user.save()

        return JsonResponse({
            'status': 201,
            'message': 'Unfollowed successfully.'
        }, status=201)


def follow_count(request, username):
    user = User.objects.get(username=username)

    return JsonResponse({
        'status': 201,
        'follower_count': user.followers.all().count(),
        'following_count': user.following.all().count(),
    }, status=200)


def like(request, post_id):
    current_user = request.user
    post = Post.objects.get(pk=post_id)

    # If targeted post is already liked by the current user, unlike
    if current_user in post.likes.all():
        post.likes.remove(current_user)
        post.save()

        return JsonResponse({
            'status': 201,
        }, status=201)

    # Else like then save
    else:
        post.likes.add(current_user)
        post.save()

        return JsonResponse({
            'status': 201,
        }, status=201)


def like_count(request, post_id):
    post = Post.objects.get(pk=post_id)

    return JsonResponse({
        'status': 201,
        'like_count': post.likes.count(),
    }, status=200)


@csrf_exempt
@login_required(redirect_field_name='login')
def new_post(request):

    if request.method == "POST":
        data = json.loads(request.body)

        content = data.get('content', '')

        if content != '':
            timestamp = datetime.now()
            user = request.user

            post = Post.objects.create(
                content=content, timestamp=timestamp, user=user)
            post.save()

            return JsonResponse({
                'status': 201,
            }, status=201)

        return JsonResponse({'error': 'Post content cannot be empty.'}, status=400)

    return JsonResponse({'error': 'Post could not be created.'}, status=400)


@csrf_exempt
@login_required
def edit_post(request, post_id):
    post = Post.objects.get(pk=post_id)

    if request.method == 'PUT':

        if request.user == post.user:

            data = json.loads(request.body)
            content = data.get('content', '')

            if content != '':
                post.content = content
                post.save()

                return JsonResponse({
                    'status': 201,
                    'new_content': content,
                }, status=201)

            return JsonResponse({'error': 'Post content cannot be empty.'}, status=400)

        return JsonResponse({'error': 'You do not own the edited post'}, status=400)

    return JsonResponse({'error': 'PUT Request method required'}, status=400)
