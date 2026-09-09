from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from groups.models import Group
from contributions.models import Contribution
from loans.models import Loan

User = get_user_model()


class LoanModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="Str0ng!Passw0rd"
        )
        self.group = Group.objects.create(name="Test Group", description="A test group", created_by=self.user)

    def test_create_loan(self):
        loan = Loan.objects.create(
            member=self.user,
            group=self.group,
            amount=500,
            reason="School fees",
        )
        self.assertEqual(loan.amount, 500)
        self.assertEqual(loan.member, self.user)
        self.assertEqual(loan.group, self.group)
        self.assertEqual(loan.status, "pending")
        self.assertIsNone(loan.approved_on)


class LoanApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.alice = User.objects.create_user(username="alice", email="alice@example.com", password="Str0ng!Passw0rd")
        self.bob = User.objects.create_user(username="bob", email="bob@example.com", password="Str0ng!Passw0rd")
        self.outsider = User.objects.create_user(
            username="outsider", email="outsider@example.com", password="Str0ng!Passw0rd"
        )

        self.client.force_authenticate(user=self.alice)
        response = self.client.post("/api/groups/", {"name": "Chama", "description": "d"})
        self.group_id = response.data["id"]
        self.group = Group.objects.get(pk=self.group_id)
        self.client.post(f"/api/groups/{self.group_id}/add_member/", {"user_id": self.bob.pk})

        Contribution.objects.create(member=self.alice, group=self.group, amount=Decimal("1000.00"))

    def test_anonymous_cannot_access_loans(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/loans/")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_member_can_request_loan_within_limit(self):
        response = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "500.00", "reason": "School fees"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")
        self.assertNotIn("email", response.data["member"])

    def test_request_exceeding_available_pool_rejected(self):
        response = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "900.00", "reason": "Too much"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_does_not_crash_with_existing_contributions(self):
        # Regression test: the original code multiplied a Decimal aggregate by a
        # Python float (0.7), which raised TypeError for any group with contributions.
        response = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "Rent"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_member_cannot_request_loan(self):
        self.client.force_authenticate(user=self.outsider)
        response = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_amount_rejected(self):
        response = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "-10.00", "reason": "x"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_group_admin_can_approve_loan(self):
        create = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"}
        )
        loan_id = create.data["id"]
        response = self.client.post(f"/api/loans/{loan_id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "approved")
        self.assertIsNotNone(response.data["approved_on"])

    def test_group_admin_can_decline_loan(self):
        create = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"}
        )
        loan_id = create.data["id"]
        response = self.client.post(f"/api/loans/{loan_id}/decline/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "declined")
        self.assertIsNone(response.data["approved_on"])

    def test_regular_member_cannot_approve_loan(self):
        create = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"}
        )
        loan_id = create.data["id"]
        self.client.force_authenticate(user=self.bob)
        response = self.client.post(f"/api/loans/{loan_id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_approve_already_decided_loan(self):
        create = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"}
        )
        loan_id = create.data["id"]
        self.client.post(f"/api/loans/{loan_id}/approve/")
        response = self.client.post(f"/api/loans/{loan_id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approved_loans_reduce_available_pool(self):
        first = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "600.00", "reason": "x"}
        )
        self.client.post(f"/api/loans/{first.data['id']}/approve/")
        second = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "300.00", "reason": "y"}
        )
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_can_withdraw_own_pending_loan(self):
        create = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"}
        )
        loan_id = create.data["id"]
        response = self.client.delete(f"/api/loans/{loan_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_member_cannot_delete_others_pending_loan(self):
        create = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"}
        )
        loan_id = create.data["id"]
        self.client.force_authenticate(user=self.bob)
        response = self.client.delete(f"/api/loans/{loan_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_decided_loan(self):
        create = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"}
        )
        loan_id = create.data["id"]
        self.client.post(f"/api/loans/{loan_id}/approve/")
        response = self.client.delete(f"/api/loans/{loan_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_loans_cannot_be_updated(self):
        create = self.client.post(
            "/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"}
        )
        loan_id = create.data["id"]
        response = self.client.patch(f"/api/loans/{loan_id}/", {"amount": "999.00"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_fellow_member_can_see_group_loans(self):
        self.client.post("/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"})
        self.client.force_authenticate(user=self.bob)
        response = self.client.get("/api/loans/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_member_sees_no_loans(self):
        self.client.post("/api/loans/", {"group": self.group_id, "amount": "100.00", "reason": "x"})
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get("/api/loans/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
