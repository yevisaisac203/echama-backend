from django.test import TestCase
from django.contrib.auth import get_user_model
from groups.models import Group
from loans.models import Loan
from datetime import date

User = get_user_model()

class LoanModelTests(TestCase):
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

    def test_create_loan(self):
        loan = Loan.objects.create(
            member=self.user,
            group=self.group,
            amount=500,
            requested_on=date.today(),
            approved_on=date.today(),
            status="pending"
        )

        self.assertEqual(loan.amount, 500)
        self.assertEqual(loan.member, self.user)
        self.assertEqual(loan.group, self.group)

    