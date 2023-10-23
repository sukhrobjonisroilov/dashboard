from django.contrib.auth.models import UserManager
from django.db import models

# Create your models here.
from  core.service.models import User,UserManager



class Xodimlar(models.Model):
    ism = models.CharField(max_length=200)
    yosh = models.IntegerField()
    lavozim = models.CharField(max_length=200)
    maosh = models.IntegerField()
    maosh_type = models.CharField(max_length=4,choices=[
        ('UZS','som'),
        ('RUB','rubl'),
        ('USD','Usd')
    ])

    def __str__(self):
        return self.ism