from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("", views.index, name="index"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),

    path("new_post", views.new_post),
    path("edit_post/<int:post_id>", views.edit_post),

    path("follow/<str:username>", views.follow, name="follow"),
    path("follow_count/<str:username>", views.follow_count),

    path("like/<int:post_id>", views.like, name="like"),
    path("like_count/<int:post_id>", views.like_count),
]
