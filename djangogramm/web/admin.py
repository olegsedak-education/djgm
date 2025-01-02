from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUser, Photo

class AppUserAdmin(UserAdmin):
    pass

admin.site.register(AppUser, AppUserAdmin)

admin.site.register(Photo)
