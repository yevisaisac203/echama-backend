from django.contrib import admin
from .models import Group, Membership


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'created_by__username')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'is_admin', 'joined_on')
    list_filter = ('is_admin',)
    search_fields = ('user__username', 'group__name')
