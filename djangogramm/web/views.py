from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import FormView
from PIL import Image as PILImage
from pathlib import Path
from io import BytesIO
import time
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.signals import thumbnail_created
from .models import Post, AppUser, UserProfile, Image, Photo
from .forms import RegisterForm, LoginForm, PostCreationForm, ImageOnPostCreationForm, PhotoForm
from djangogramm.settings.web.base import MAX_IMAGE_SIZE , IMAGE_QUALITY, MEDIA_ROOT
from django.core.files.base import ContentFile


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


def convert_and_save_image(image_obj):
    optimised_image_size = (MAX_IMAGE_SIZE, MAX_IMAGE_SIZE)
    original_image_path = Path(image_obj.image.path)
    image = PILImage.open(original_image_path)


    if image.height > MAX_IMAGE_SIZE or image.width > MAX_IMAGE_SIZE:
        image.thumbnail(optimised_image_size, PILImage.LANCZOS)

    new_image_filename = generate_short_standart_img_filename(original_image_path.stem)
    output_path = original_image_path.with_name(new_image_filename).with_suffix('.webp')

    image_io = BytesIO()
    image.save(image_io, format='WEBP', quality=IMAGE_QUALITY)
    new_image_content = ContentFile(image_io.getvalue())

    image_obj.image.save(new_image_filename, new_image_content)

    if original_image_path.exists() and original_image_path.suffix != '.webp':
        original_image_path.unlink()

    return output_path

def generate_short_standart_img_filename(filename):

    timestamp = time.strftime('%Y%m%d%H%M%S')
    new_filename = f"img_{timestamp}.webp"

    return new_filename


@login_required
def create_post(request):
    if request.method == 'POST':
        post_form = PostCreationForm(request.POST)
        image_form = ImageOnPostCreationForm(request.POST,request.FILES)

        if post_form.is_valid() and image_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()

            images = request.FILES.getlist('image')

            print(f"FILES: {request.FILES}")
            print(f"getlist('image'): {request.FILES.getlist('image')}")
            for image in images:
                new_image = Image.objects.create(image=image)
                output_path = convert_and_save_image(new_image)
                new_image.image.name = str(output_path.relative_to(MEDIA_ROOT))
                post.images.add(new_image)

            messages.success(request,'Post created successfully')
            return redirect('posts_list')

    post_form = PostCreationForm()
    image_form = ImageOnPostCreationForm()

    context = {
        'post_form': post_form,
        'image_form': image_form,
    }
    return render(request, 'create_post.html', context)
    # upload(request)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, "post_detail.html", {'post': post})


def users_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("403 Forbidden: Access denied")
    users = AppUser.objects.all()
    return render(request, 'users_list.html')

def upload(request):
    context = dict( backend_form = PhotoForm())

    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # return redirect('display')
            return redirect('posts_list')

    # return  render(request, 'upload.html', context)
    return  render(request, 'create_post.html', context)

def display(request):
    photos = Photo.objects.all()
    # return render(request, 'display.html', {'photos': photos})
    return render(request, 'post_detail.html', {'photos': photos})


