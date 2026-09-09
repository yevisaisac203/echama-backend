from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from groups.models import Group, Membership
from contributions.models import Contribution

User = get_user_model()


class ContributionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="Str0ng!Passw0rd"
        )
        self.group = Group.objects.create(name="Test Group", description="A test group", created_by=self.user)

    def test_create_contribution(self):
        contribution = Contribution.objects.create(member=self.user, group=self.group, amount=100)
        self.assertEqual(contribution.amount, 100)
        self.assertEqual(contribution.group, self.group)
        self.assertEqual(contribution.member, self.user)
        self.assertIsNotNone(contribution.date)

    def test_date_is_always_server_assigned(self):
        contribution = Contribution.objects.create(member=self.user, group=self.group, amount=50)
        self.assertIsNotNone(contribution.date)


class ContributionApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.alice = User.objects.create_user(username="alice", email="alice@example.com", password="Str0ng!Passw0rd")
        self.bob = User.objects.create_user(username="bob", email="bob@example.com", password="Str0ng!Passw0rd")
        self.outsider = User.objects.create_user(
            username="outsider", email="outsider@example.com", password="Str0ng!Passw0rd"
        )
        self.staff = User.objects.create_user(
            username="staff", email="staff@example.com", password="Str0ng!Passw0rd", role="admin", is_staff=True
        )

        self.client.force_authenticate(user=self.alice)
        response = self.client.post("/api/groups/", {"name": "Chama", "description": "d"})
        self.group_id = response.data["id"]
        self.client.post(f"/api/groups/{self.group_id}/add_member/", {"user_id": self.bob.pk})

    def test_anonymous_cannot_access_contributions(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/contributions/")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_member_can_record_contribution(self):
        response = self.client.post("/api/contributions/", {"group": self.group_id, "amount": "100.00"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data["amount"]), Decimal("100.00"))
        self.assertEqual(response.data["member"]["username"], "alice")
        self.assertNotIn("email", response.data["member"])

    def test_non_member_cannot_record_contribution_for_group(self):
        self.client.force_authenticate(user=self.outsider)
        response = self.client.post("/api/contributions/", {"group": self.group_id, "amount": "100.00"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_or_negative_amount_rejected(self):
        response = self.client.post("/api/contributions/", {"group": self.group_id, "amount": "0.00"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_date_cannot_be_backdated_by_client(self):
        response = self.client.post(
            "/api/contributions/",
            {"group": self.group_id, "amount": "10.00", "date": "2000-01-01T00:00:00Z"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["date"].startswith("2000-01-01"))

    def test_fellow_group_member_can_see_contribution(self):
        self.client.post("/api/contributions/", {"group": self.group_id, "amount": "100.00"})
        self.client.force_authenticate(user=self.bob)
        response = self.client.get("/api/contributions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_member_cannot_see_group_contributions(self):
        self.client.post("/api/contributions/", {"group": self.group_id, "amount": "100.00"})
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get("/api/contributions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_contribution_cannot_be_updated(self):
        create = self.client.post("/api/contributions/", {"group": self.group_id, "amount": "100.00"})
        contribution_id = create.data["id"]
        response = self.client.patch(f"/api/contributions/{contribution_id}/", {"amount": "999.00"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_regular_member_cannot_delete_contribution(self):
        create = self.client.post("/api/contributions/", {"group": self.group_id, "amount": "100.00"})
        contribution_id = create.data["id"]
        self.client.force_authenticate(user=self.bob)
        response = self.client.delete(f"/api/contributions/{contribution_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_admin_can_delete_contribution(self):
        create = self.client.post("/api/contributions/", {"group": self.group_id, "amount": "100.00"})
        contribution_id = create.data["id"]
        response = self.client.delete(f"/api/contributions/{contribution_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deleting_group_with_contributions_is_protected(self):
        self.client.post("/api/contributions/", {"group": self.group_id, "amount": "100.00"})
        response = self.client.delete(f"/api/groups/{self.group_id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deleting_user_with_contributions_is_protected(self):
        self.client.post("/api/contributions/", {"group": self.group_id, "amount": "100.00"})
        response = self.client.delete(f"/api/users/{self.alice.pk}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
