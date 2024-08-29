# main/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    model = User
    # Define fields to display in admin here
    # ...

admin.site.register(User, UserAdmin)
