from django.contrib import admin
from .models import Contribution


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('member', 'group', 'amount', 'date')
    list_filter = ('group',)
    search_fields = ('member__username', 'group__name')
