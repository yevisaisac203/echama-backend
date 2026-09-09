from django.db import IntegrityError, transaction
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from .models import Group, Membership

User = get_user_model()


class GroupModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Str0ng!Passw0rd",
        )

    def test_create_group(self):
        group = Group.objects.create(
            name="Savings Group",
            description="A group for savings",
            created_by=self.user,
        )
        self.assertEqual(group.name, "Savings Group")
        self.assertEqual(group.description, "A group for savings")

    def test_membership_is_unique_per_user_and_group(self):
        group = Group.objects.create(name="G", description="d", created_by=self.user)
        Membership.objects.create(user=self.user, group=group)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Membership.objects.create(user=self.user, group=group)

    def test_deleting_user_with_groups_is_protected(self):
        from django.db.models import ProtectedError
        Group.objects.create(name="G", description="d", created_by=self.user)
        with self.assertRaises(ProtectedError):
            self.user.delete()


class GroupApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(username="alice", email="alice@example.com", password="Str0ng!Passw0rd")
        self.bob = User.objects.create_user(username="bob", email="bob@example.com", password="Str0ng!Passw0rd")
        self.carol = User.objects.create_user(username="carol", email="carol@example.com", password="Str0ng!Passw0rd")
        self.staff = User.objects.create_user(
            username="staff", email="staff@example.com", password="Str0ng!Passw0rd", role="admin", is_staff=True
        )

    def create_group(self, owner):
        self.client.force_authenticate(user=owner)
        response = self.client.post("/api/groups/", {"name": "Chama", "description": "test group"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data["id"]

    def test_anonymous_cannot_access_groups(self):
        response = self.client.get("/api/groups/")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_creator_becomes_admin_member(self):
        group_id = self.create_group(self.alice)
        self.assertTrue(Membership.objects.filter(group_id=group_id, user=self.alice, is_admin=True).exists())

    def test_non_member_cannot_see_group(self):
        group_id = self.create_group(self.alice)
        self.client.force_authenticate(user=self.bob)
        response = self.client.get(f"/api/groups/{group_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_only_shows_own_groups(self):
        self.create_group(self.alice)
        self.client.force_authenticate(user=self.bob)
        self.create_group(self.bob)
        response = self.client.get("/api/groups/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_staff_sees_all_groups(self):
        self.create_group(self.alice)
        self.create_group(self.bob)
        self.client.force_authenticate(user=self.staff)
        response = self.client.get("/api/groups/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_can_add_member(self):
        group_id = self.create_group(self.alice)
        response = self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.bob.pk})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Membership.objects.filter(group_id=group_id, user=self.bob).exists())

    def test_cannot_add_same_member_twice(self):
        group_id = self.create_group(self.alice)
        self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.bob.pk})
        response = self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.bob.pk})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_member_cannot_add_member(self):
        group_id = self.create_group(self.alice)
        self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.bob.pk})
        self.client.force_authenticate(user=self.bob)
        response = self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.carol.pk})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_member_cannot_update_group(self):
        group_id = self.create_group(self.alice)
        self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.bob.pk})
        self.client.force_authenticate(user=self.bob)
        response = self.client.patch(f"/api/groups/{group_id}/", {"name": "Hijacked"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_remove_member(self):
        group_id = self.create_group(self.alice)
        self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.bob.pk})
        response = self.client.post(f"/api/groups/{group_id}/remove_member/", {"user_id": self.bob.pk})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Membership.objects.filter(group_id=group_id, user=self.bob).exists())

    def test_cannot_remove_last_admin(self):
        group_id = self.create_group(self.alice)
        self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.bob.pk})
        response = self.client.post(f"/api/groups/{group_id}/remove_member/", {"user_id": self.alice.pk})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_can_leave_group(self):
        group_id = self.create_group(self.alice)
        self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.bob.pk})
        self.client.force_authenticate(user=self.bob)
        response = self.client.post(f"/api/groups/{group_id}/leave/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_sole_admin_cannot_leave_while_other_members_remain(self):
        group_id = self.create_group(self.alice)
        self.client.post(f"/api/groups/{group_id}/add_member/", {"user_id": self.bob.pk})
        response = self.client.post(f"/api/groups/{group_id}/leave/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_list_does_not_expose_email(self):
        group_id = self.create_group(self.alice)
        response = self.client.get(f"/api/groups/{group_id}/")
        self.assertNotIn("email", response.data["members"][0]["user"])
