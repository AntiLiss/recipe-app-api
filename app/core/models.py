from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **other_fields):
        if not email:
            raise ValueError("User must have an email!")
        user = self.model(email=self.normalize_email(email), **other_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **other_fields):
        if not email:
            raise ValueError("User must have an email!")
        user = self.model(email=self.normalize_email(email), **other_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    time_minutes = models.DecimalField(max_digits=4, decimal_places=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField(blank=True)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(to='Tag', blank=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.name
