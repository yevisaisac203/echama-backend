from django.core.cache import cache
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Str0ng!Passw0rd",
        )

    def test_create_user(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("Str0ng!Passw0rd"))

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), "testuser")

    def test_email_must_be_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="other",
                email="test@example.com",
                password="Str0ng!Passw0rd",
            )


class RegistrationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.url = "/api/users/register/"

    def test_anonymous_can_register(self):
        response = self.client.post(self.url, {
            "username": "newmember",
            "email": "new@example.com",
            "password": "Str0ng!Passw0rd",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newmember").exists())
        self.assertNotIn("password", response.data)

    def test_weak_password_rejected(self):
        response = self.client.post(self.url, {
            "username": "weakpass",
            "email": "weak@example.com",
            "password": "password",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="weakpass").exists())

    def test_duplicate_email_rejected(self):
        User.objects.create_user(username="first", email="dup@example.com", password="Str0ng!Passw0rd")
        response = self.client.post(self.url, {
            "username": "second",
            "email": "dup@example.com",
            "password": "Str0ng!Passw0rd",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_cannot_set_role(self):
        response = self.client.post(self.url, {
            "username": "sneaky",
            "email": "sneaky@example.com",
            "password": "Str0ng!Passw0rd",
            "role": "admin",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username="sneaky").role, "member")


class UserPermissionTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.alice = User.objects.create_user(username="alice", email="alice@example.com", password="Str0ng!Passw0rd")
        self.bob = User.objects.create_user(username="bob", email="bob@example.com", password="Str0ng!Passw0rd")
        self.admin = User.objects.create_user(
            username="admin", email="admin@example.com", password="Str0ng!Passw0rd", role="admin", is_staff=True
        )

    def test_anonymous_cannot_list_users(self):
        response = self.client.get("/api/users/")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_anonymous_cannot_modify_user(self):
        response = self.client.patch(f"/api/users/{self.alice.pk}/", {"email": "hacked@example.com"})
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.email, "alice@example.com")

    def test_regular_user_cannot_list_all_users(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {u["username"] for u in response.data}
        self.assertEqual(usernames, {"alice"})

    def test_regular_user_cannot_edit_other_user(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.patch(f"/api/users/{self.bob.pk}/", {"email": "hacked@example.com"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.bob.refresh_from_db()
        self.assertEqual(self.bob.email, "bob@example.com")

    def test_regular_user_can_edit_self(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.patch(f"/api/users/{self.alice.pk}/", {"first_name": "Alice"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.first_name, "Alice")

    def test_regular_user_cannot_delete_other_user(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.delete(f"/api/users/{self.bob.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(User.objects.filter(pk=self.bob.pk).exists())

    def test_admin_can_list_and_manage_all_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {u["username"] for u in response.data}
        self.assertEqual(usernames, {"alice", "bob", "admin"})


class JWTAuthFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(username="carol", email="carol@example.com", password="Str0ng!Passw0rd")

    def test_login_and_refresh(self):
        response = self.client.post("/api/token/", {"username": "carol", "password": "Str0ng!Passw0rd"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        refresh_response = self.client.post("/api/token/refresh/", {"refresh": response.data["refresh"]})
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post("/api/token/", {"username": "carol", "password": "wrong"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh_token(self):
        login = self.client.post("/api/token/", {"username": "carol", "password": "Str0ng!Passw0rd"})
        refresh_token = login.data["refresh"]

        self.client.force_authenticate(user=self.user)
        logout_response = self.client.post("/api/token/logout/", {"refresh": refresh_token})
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        self.client.force_authenticate(user=None)
        reuse_response = self.client.post("/api/token/refresh/", {"refresh": refresh_token})
        self.assertEqual(reuse_response.status_code, status.HTTP_401_UNAUTHORIZED)
