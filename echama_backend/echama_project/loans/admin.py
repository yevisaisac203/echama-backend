from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('member', 'group', 'amount', 'status', 'requested_on', 'approved_on')
    list_filter = ('status', 'group')
    search_fields = ('member__username', 'group__name')
