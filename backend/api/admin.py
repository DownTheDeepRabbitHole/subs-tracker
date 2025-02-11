from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User, Category, Subscription, Plan, UserPlan

class CustomUserAdmin(UserAdmin):
    model = User
    # Add custom fields like 'remember_me', 'allow_notifications', and 'api_key_encrypted'
    list_display = ['username', 'email', 'first_name', 'last_name', 'remember_me', 'allow_notifications']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('remember_me', 'allow_notifications', 'api_key_encrypted')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('remember_me', 'allow_notifications', 'api_key_encrypted')}),
    )

admin.site.register(User, CustomUserAdmin)

admin.site.register(Category)
admin.site.register(Subscription)
admin.site.register(Plan)
admin.site.register(UserPlan)