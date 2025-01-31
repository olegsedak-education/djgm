from django.urls import path, include
from django.views.generic.base import TemplateView
from django.contrib.auth.views import LogoutView
from django.conf import settings
from . import views


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("accounts/",
         include([
             path("register/", views.sign_up, name="register"),
             path("login/", views.sign_in, name="login"),
             path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
             ])
         ),
    path("users/",
         include([
             path("", views.users_list, name="users_list"),
             path("<int:user_id>/",
                  include([
                      path("",views.user_profile, name="user_profile"),
                      path("follow/", views.follow_user, name="follow_user"),
                      path("unfollow/", views.unfollow_user, name="unfollow_user"),
                  ])
            ),
             ])
         ),
    path("posts/",
         include([
             path("", views.posts_list, name="posts_list"),
             path("create/", views.create_post, name="create_post"),
             path("<int:post_id>/",
                  include([
                      path("", views.post_detail, name="post_detail"),
                      path("like/", views.like_post, name="like_post"),
                      path("unlike/", views.unlike_post, name="unlike_post"),
                      path("dislike/", views.dislike_post, name="dislike_post"),
                      path("undislike/", views.undislike_post, name="undislike_post")
                  ]),
              ),
         ]),
    ),
    path("feed/", views.feed, name="feed"),
]

