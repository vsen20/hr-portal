from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Organization", {"fields": ("organization",)}),
    )
    list_display = DjangoUserAdmin.list_display + ("organization",)
