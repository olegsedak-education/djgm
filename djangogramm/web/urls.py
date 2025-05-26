from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.views.generic.base import TemplateView
from . import views


app_name = 'web'

auth_patterns = [
    path("register/", views.sign_up, name="register"),
    path("register/complete/<uid64>/<str:token>/", views.complete_registration, name="complete_registration"),
    path("login/", views.sign_in, name="login"),
    path("logout/", LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name="logout"),
]

user_patterns = [
    path("", views.users_list, name="list"),
    path("<int:pk>/", views.user_profile, name="detail"),
    path("<int:pk>/follow/", views.follow_user, name="follow"),
    path("<int:pk>/unfollow/", views.unfollow_user, name="unfollow"),
    path("<int:pk>/followers/", views.followers_list, name="followers"),
    path("<int:pk>/following/", views.following_list, name="following"),
    path("<int:pk>/edit/", views.edit_profile, name="edit_profile"),
]

post_patterns = [
    path("", views.posts_list, name="list"),
    path("create/", views.create_post, name="create"),
    path("<int:pk>/", views.post_detail, name="detail"),
    path("<int:pk>/edit/", views.edit_post, name="edit"),
    path("<int:pk>/delete/", views.delete_post, name="delete"),
    path("<int:pk>/like/", views.like_post, name="like"),
    path("<int:pk>/unlike/", views.unlike_post, name="unlike"),
    path("<int:pk>/dislike/", views.dislike_post, name="dislike"),
    path("<int:pk>/undislike/", views.undislike_post, name="undislike"),
    path("tag/<str:tag_name>/", views.posts_by_tag, name="by_tag"),
]

tag_patterns = [
    path("", views.tag_list, name="list"),
]

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("about/", views.about, name="about"),
    path("accounts/", include((auth_patterns, "auth"))),
    path("users/", include((user_patterns, "users"))),
    path("posts/", include((post_patterns, "posts"))),
    path("tags/", include((tag_patterns, "tags"))),
    path("feed/", views.feed, name="feed"),
]
