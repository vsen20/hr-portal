from django.contrib.auth.models import AbstractUser
from django.db import models
from platform_core.models import Organization


class User(AbstractUser):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users'
    )

    def __str__(self):
        return self.username
