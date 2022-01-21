from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):
    follower = models.ManyToManyField(
        'User', blank=True, related_name='following')
    followed = models.ManyToManyField(
        'User', blank=True, related_name='followers')


class Post(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now())

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='creator')
    likes = models.ManyToManyField(
        User, blank=True, related_name='likers')
