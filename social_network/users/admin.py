from django.contrib import admin
from .models import User, FriendRequest

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    search_fields = ('sender__email', 'receiver__email', 'status')

admin.site.register(User)
admin.site.register(FriendRequest, FriendRequestAdmin)