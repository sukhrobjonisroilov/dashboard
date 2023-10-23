from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin

from django.db import models
from methodism.models import Otp


class CManager(UserManager):
    def create_user(self, username, email, password, is_staff=False, is_active =True,is_superuser=False, **extra_fields):
        user = self.model(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(str(password))
        user.save()
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        return self.create_user(username=username,password=password, email=email, is_staff=True, is_superuser=True, **extra_fields)


class User(AbstractBaseUser,PermissionsMixin):
    fio = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class OtpToken(Otp):
    email = models.EmailField(max_length=200)

