from datetime import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django_enumfield.enum import Enum, EnumField
from django.conf import settings
from cloudinary.models import CloudinaryField


class Photo(models.Model):
    image = CloudinaryField('image')


class AppUser(AbstractUser):
    avatar = models.ImageField(upload_to=settings.IMAGE_DIR, default=settings.DEFAULT_AVATAR_IMG_PATH)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='app_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='app_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE, db_index=True)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} profile"


class ReactionType(Enum):
    NEUTRAL = 0
    LIKE = 1
    DISLIKE = - 1


    __labels__ = {
        LIKE: "Like",
        DISLIKE: "Dislike",
        NEUTRAL: "Neutral",
    }

    __default__ = NEUTRAL


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    uploadede_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.url


class Post(models.Model):
    author = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    images = models.ManyToManyField(Image, related_name='posts')

    def __str__(self):
        return f'{self.title}, {self.author}, {self.text}, {self.created_at}, {self.updated_at}'

class Comment(models.Model):
    author = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.text}, {self.author.username}, {self.post.title}'


class PostReaction(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reaction = EnumField(ReactionType, default=ReactionType.default())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_reaction_type(self):
        return self.reaction.label

    def __str__(self):
        return f"PostReaction: {self.get_reaction_type()} by {self.user.username} on {self.post.title}"


class CommentReaction(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reaction = EnumField(ReactionType, default=ReactionType.default())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_reaction_type(self):
        return self.reaction.label

    def __str__(self):
        return f"CommentReaction: {self.get_reaction_type()} by {self.user.username} on {self.comment.text}"


class Tag(models.Model):
    name = models.CharField(max_length=50)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
