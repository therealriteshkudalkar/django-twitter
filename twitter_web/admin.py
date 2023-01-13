from django.contrib import admin
from .models import User

# admin.site.register(User)


class UserAdmin(admin.ModelAdmin):
    list_display = ['fname', 'lname', 'username', 'is_verified']
    list_filter = ['username', 'created_at']
    fields = ['fname', 'lname', 'username', 'is_verified']


admin.site.register(User, UserAdmin)
