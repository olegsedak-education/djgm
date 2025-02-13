from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import FormView
from pathlib import Path
import time
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.signals import thumbnail_created
from .models import Post, AppUser, UserProfile, Image, PostReaction, ReactionType, Following
from .forms import RegisterForm, LoginForm ,PostForm
from djangogramm.settings.web.base import MAX_IMAGE_SIZE , IMAGE_QUALITY, MEDIA_ROOT, CLOUDINARY_STORAGE
from django.core.files.base import ContentFile
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())



def sign_up(request):
    if request.method == "GET":
        form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, "You have signed up succesfully.")
            login(request, user)
            return redirect("home")
    return render(request, 'register.html', { "form": form })


def sign_in(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Hi {username.title()}, welcome back.")
                return redirect("home")
        messages.error(request, f"Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def posts_list(request):
    posts = Post.objects.all().order_by('created_at')
    return render(request, 'posts_list.html', {'posts': posts})


def feed(request):
    return render(request, "feed.html")


def user_profile(request, user_id=None):
    user = get_object_or_404(AppUser, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    return render(request, "user_profile.html", {'user': user, 'profile': profile})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, "post_detail.html", {'post': post})


def users_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("403 Forbidden: Access denied")
    users = AppUser.objects.all()
    return render(request, 'users_list.html')

@login_required
def create_post(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)

        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()

            images_urls = request.POST.get('image_urls', '').split(',')
            for url in images_urls:
                if url.strip():
                    image = Image.objects.create(image=url.strip())
                    post.images.add(image)
            post.save()
            return redirect('post_detail', post_id=post.id)
        else:
            print("Ошибки формы:", post_form.errors)

            return render(request, 'create_post.html', {'post_form': post_form})

    else:
        post_form = PostForm()

    return render(request, 'create_post.html', {
        'post_form': post_form,
        'cloud_name': CLOUDINARY_STORAGE['CLOUD_NAME'],
        'upload_preset': CLOUDINARY_STORAGE['UPLOAD_PRESET'],
    })

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(AppUser, userbame=username)
    if request.user == user_to_follow:
        messages.error(request, "You can't follow yourself!")
        return redirect('user_profile', username=username)

    Following.objects.get_or_create(
            user=request.user,
            following_user=user_to_follow
        )
    return redirect('user_profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(AppUser, username=username)
    if request.user == user_to_unfollow:
        messages.error(request, "You cannot unfollow yourself.")
        return redirect('user_profile', username=username)
    Following.objects.filter(
        user=request.user,
        following_user=user_to_unfollow
    ).delete()
    return redirect('user_profile', username=username)


@login_required
def post_reaction_handler(request, post_id, reaction_type):
    post = get_object_or_404(Post, id=post_id)
    reaction, _ = PostReaction.objects.update_or_create(
        user=request.user,
        post=post,
        defaults={'reaction': reaction_type}
    )
    return redirect('post_detail', post_id=post.id)


@login_required
def like_post(request, post_id):
    return post_reaction_handler(request, post_id, ReactionType.LIKE)


@login_required
def dislike_post(request, post_id):
    return post_reaction_handler(request, post_id, ReactionType.DISLIKE)

@login_required
def unlike_post(request, post_id):
    PostReaction.objects.filter(
        user=request.user,
        post__id=post_id,
    ).delete()
    return redirect('post_detail', post_id=post_id)

@login_required
def undislike_post(request, post_id):
    PostReaction.objects.filter(
        user=request.user,
        post__id=post_id,
        reaction=ReactionType.DISLIKE
    ).delete()
    return redirect('post_detail', post_id=post_id)










