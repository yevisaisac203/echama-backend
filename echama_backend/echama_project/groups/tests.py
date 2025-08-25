from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Group

User = get_user_model()

class GroupModelTests(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

    def test_create_group(self):
        group = Group.objects.create(
            name="Savings Group",
            description="A group for savings",
            created_by= self.user,
            
        )

        self.assertEqual(group.name, "Savings Group")
        self.assertEqual(group.description, "A group for savings")
