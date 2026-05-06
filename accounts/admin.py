from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'city', 'is_active', 'date_joined')
    list_filter = ('role', 'city', 'is_active')
    search_fields = ('username', 'email', 'last_name', 'first_name', 'phone')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone', 'patronymic', 'role', 'city', 'address', 'avatar')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'phone', 'patronymic', 'role', 'city', 'address')
        }),
    )
