from django.test import TestCase
from django.contrib.auth import get_user_model
from groups.models import Group
from contributions.models import Contribution
from datetime import date

User = get_user_model()

class ContributionModelTests(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )

       
        self.group = Group.objects.create(
            name="Test Group",
            description="A test group",
            created_by=self.user
        )

    def test_create_contribution(self):
       
        contribution = Contribution.objects.create(
            member=self.user,
            group=self.group,
            amount=100,
            date=date.today()  )

        
        self.assertEqual(contribution.amount, 100)
        self.assertEqual(contribution.group, self.group)
        self.assertEqual(contribution.member, self.user)
        self.assertEqual(contribution.date, date.today())
