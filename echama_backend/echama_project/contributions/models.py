from django.db import models
from users.models import User
from groups.models import Group

class Contribution(models.Model):
    member = models.ForeignKey(User, on_delete = models.CASCADE)
    group = models.ForeignKey(Group, on_delete = models.CASCADE )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_created=True)

