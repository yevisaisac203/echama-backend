from django.db import models
from users.models import User
from groups.models import Group


class Loan(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )
    member = models.ForeignKey(User, on_delete=models.PROTECT, related_name='loans')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_on = models.DateTimeField(auto_now_add=True)
    approved_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_on']

    def __str__(self):
        return f'{self.member} - {self.amount} ({self.status})'
