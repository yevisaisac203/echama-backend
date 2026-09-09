from django.db import models
from users.models import User
from groups.models import Group


class Contribution(models.Model):
    member = models.ForeignKey(User, on_delete=models.PROTECT, related_name='contributions')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.member} - {self.amount} ({self.group})'
