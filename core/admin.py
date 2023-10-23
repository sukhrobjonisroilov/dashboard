from django.contrib import admin
from .service.view import User
from .models import Xodimlar
# Register your models here.
admin.site.register(User)
admin.site.register(Xodimlar)