from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    photo = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True
    )
    favorite_team = models.ForeignKey(
        'football.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fans',
        verbose_name='Seleção favorita'
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"