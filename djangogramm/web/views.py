from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from djangogramm.settings.web.base import MAX_IMAGE_SIZE, IMAGE_QUALITY, MEDIA_ROOT, CLOUDINARY_STORAGE
from dotenv import load_dotenv, find_dotenv

from .forms import RegisterForm, LoginForm, PostForm, UserProfileForm
from .models import Post, AppUser, UserProfile, Image, PostReaction, ReactionType, Following, Tag

load_dotenv(find_dotenv())


def sign_up(request):
    if request.method == "GET":
        form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = False
            user.save()

            UserProfile.objects.create(user=user)

            send_confirmation_email(request, user)

            messages.success(request, "Registration successful! Please check your email to confirm your account.")
            return redirect('web:auth:login')
    return render(request, 'register.html', {"form": form})


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
                return redirect('web:home')
        messages.error(request, f"Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def posts_list(request):
    posts = Post.objects.all().order_by('created_at')
    return render(request, 'posts_list.html', {'posts': posts})


def feed(request):
    following_ids = Following.objects.filter(
        user=request.user
    ).values_list('following_user_id', flat=True)

    following_ids = list(following_ids) + [request.user.id]

    posts = Post.objects.filter(
        author_id__in=following_ids
    ).select_related('author').prefetch_related(
        'tags', 'images', 'postreaction_set'
    ).order_by('-created_at')

    return render(request, "feed.html", {'posts': posts})


@login_required
def user_profile(request, pk):
    user = get_object_or_404(AppUser, pk=pk)
    profile, created = UserProfile.objects.get_or_create(user=user)
    return render(request, "user_profile.html", {'user': user, 'profile': profile})

    if request.user != user:
        return HttpResponseForbidden("403 Forbidden: You can only edit your own profile")

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save(user=user)
            messages.success(request, "Profile updated successfully.")
            return redirect('web:users:detail', pk=user.pk)
    else:
        form = UserProfileForm(instance=profile, user=user)

    return render(request, 'edit_profile.html', {'form': form, 'user': user})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    user_reaction = None
    if request.user.is_authenticated:
        reaction = PostReaction.objects.filter(
            user=request.user,
            post=post
        ).first()

        if reaction:
            user_reaction = reaction.reaction.value
    context = {'post': post, 'user_reaction': user_reaction, }

    return render(request, "post_detail.html", context)


def users_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("403 Forbidden: Access denied")
    users = AppUser.objects.all()
    return render(request, 'users_list.html', {'users': users})


@login_required
def create_post(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)

        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            post_form.save()

            images_urls = request.POST.get('image_urls', '').split(',')
            for url in images_urls:
                if url.strip():
                    image = Image.objects.create(image=url.strip())
                    post.images.add(image)
            post.save()
            return redirect('web:posts:detail', pk=post.id)
        else:
            return render(request, 'create_post.html', {'post_form': post_form})

    else:
        post_form = PostForm()

    return render(request, 'create_post.html', {
        'post_form': post_form,
        'cloud_name': CLOUDINARY_STORAGE['CLOUD_NAME'],
        'upload_preset': CLOUDINARY_STORAGE['UPLOAD_PRESET'],
    })


@login_required
def follow_user(request, pk):
    user_to_follow = get_object_or_404(AppUser, pk=pk)

    if request.user == user_to_follow:
        messages.error(request, "You can't follow yourself!")
        return redirect('web:users:detail', pk=pk)

    following_obj, created = Following.objects.get_or_create(
        user=request.user,
        following_user=user_to_follow
    )

    if created:
        messages.success(request, f"You are now following {user_to_follow.username}!")
    else:
        messages.info(request, f"You already follow {user_to_follow.username}.")

    return redirect('web:users:detail', pk=pk)


@login_required
def unfollow_user(request, pk):
    user_to_unfollow = get_object_or_404(AppUser, pk=pk)
    if request.user == user_to_unfollow:
        messages.error(request, "You cannot unfollow yourself.")
        return redirect('web:users:detail', pk=pk)
    Following.objects.filter(
        user=request.user,
        following_user=user_to_unfollow
    ).delete()
    return redirect('web:users:detail', pk=pk)


@login_required
def post_reaction_handler(request, pk, reaction_type):
    post = get_object_or_404(Post, id=pk)
    reaction, created = PostReaction.objects.update_or_create(
        user=request.user,
        post=post,
        defaults={'reaction': reaction_type}
    )
    if not created and reaction.reaction == reaction_type:
        reaction.delete()
    else:
        reaction.reaction = reaction_type
        reaction.save()
    return redirect('web:posts:detail', pk=post.id)


@login_required
def like_post(request, pk):
    return post_reaction_handler(request, pk, ReactionType.LIKE)


@login_required
def dislike_post(request, pk):
    return post_reaction_handler(request, pk, ReactionType.DISLIKE)


@login_required
def unlike_post(request, pk):
    PostReaction.objects.filter(
        user=request.user,
        post__id=pk,
    ).delete()
    return redirect('web:posts:detail', pk=pk)


@login_required
def undislike_post(request, pk):
    PostReaction.objects.filter(
        user=request.user,
        post__id=pk,
        reaction=ReactionType.DISLIKE
    ).delete()
    return redirect('web:posts:detail', pk=pk)


def about(request):
    return render(request, 'about.html')


def send_confirmation_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
    domain = get_current_site(request).domain
    activation_link = f"http://{domain}{reverse('web:auth:complete_registration',
                                                kwargs={'uid64': uid, 'token': token})}"

    subject = "Confirm your email"
    message = render_to_string('email_confirmation.html',
                               {'user': user, 'activation_link': activation_link})
    text_message = f"Confirm your email\n\nHello {user.username},\n\nPlease confirm your email by clicking the link below:\n{activation_link}"

    send_mail(
        subject=subject,
        message=text_message,
        from_email='noreply@djangogramm.pp.ua',
        recipient_list=[user.email],
        html_message=message
    )


def complete_registration(request, uid64, token):
    try:

        uid = force_str(urlsafe_base64_decode(uid64))
        user = AppUser.objects.get(pk=uid)

        if user.is_active and user.is_email_confirmed:
            messages.info(request, "Email was already confirmed. You can login to your account.")
            return redirect('web:auth:login')

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_email_confirmed = True
            user.save()
            messages.success(request, "Email confirmed successfully. Please login to your account.")
            return redirect('web:auth:login')
        else:
            print("Invalid token")
            messages.error(request, "The confirmation link has expired. Please request a new one.")
            return redirect('web:auth:register')

    except (TypeError, ValueError, OverflowError) as e:
        print(f"Decoding error: {str(e)}")
        messages.error(request, "Invalid confirmation link format.")
        return redirect('web:auth:register')
    except AppUser.DoesNotExist as e:
        print(f"User not found: {str(e)}")
        messages.error(request, "User account not found. Please register again.")
        return redirect('web:auth:register')


@login_required
def edit_profile(request, pk):
    if int(pk) != request.user.pk:
        messages.error(request, "You can only edit your own profile.")
        return redirect('web:users:detail', pk=request.user.pk)

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user_profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('web:users:detail', pk=request.user.pk)
    else:
        form = UserProfileForm(instance=user_profile, user=request.user)

    return render(request, 'user_profile_edit.html', {'form': form, 'profile': user_profile})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    if post.author != request.user:
        messages.error(request, "You can't edit this post!")
        return redirect('web:posts:detail', pk=post.id)

    if request.method == 'POST':
        post_form = PostForm(request.POST, instance=post)
        if post_form.is_valid():
            post = post_form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('web:posts:detail', pk=post.id)
    else:
        initial_data = {
            'title': post.title,
            'text': post.text,
            'tags': ', '.join(tag.name for tag in post.tags.all())
        }
        post_form = PostForm(instance=post, initial=initial_data)

    return render(request, 'edit_post.html', {
        'post_form': post_form,
        'post': post
    })


def posts_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name.lower())
    posts = Post.objects.filter(tags=tag).order_by('-created_at')
    return render(request, 'posts_list.html', {
        'posts': posts,
        'tag': tag
    })


def tag_list(request):
    tags = Tag.objects.all().order_by('name')
    return render(request, 'tag_list.html', {'tags': tags})


@login_required
def followers_list(request, username):
    user = get_object_or_404(AppUser, username=username)
    followers = Following.objects.filter(following_user=user).select_related('user')
    return render(request, 'followers_list.html', {
        'user': user,
        'followers': followers
    })


@login_required
def following_list(request, username):
    user = get_object_or_404(AppUser, username=username)
    following = Following.objects.filter(user=user).select_related('following_user')
    return render(request, 'following_list.html', {
        'user': user,
        'following': following
    })


def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    is_following = False

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following_user=user
        ).exists()

    followers_count = Follow.objects.filter(following_user=user).count()
    following_count = Follow.objects.filter(follower=user).count()

    context = {
        'user': user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    return render(request, 'user_detail.html', context)


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.author != request.user:
        messages.error(request, "You can't delete this post!")
        return redirect('web:posts:detail', pk=post.id)
    post.delete()
    return redirect('web:posts:list')
