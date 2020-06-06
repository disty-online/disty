from django.test import TestCase
from disty.models import Role, User

# Create your tests here.


class ModelsTestCase(TestCase):
    def setUp(self):
        Role.objects.create(role_name="admin")
        User.objects.create(
            name="admin_user", password="password", role=Role.objects.get(pk=1)
        )

    def test_create(self):
        admin = Role.objects.get(role_name="admin")
        assert admin.role_name == "admin"

    def test_create(self):
        admin = User.objects.get(name="admin_user")
        assert admin.role_id == 1
