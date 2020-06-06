import datetime
from django.test import TestCase
from django.utils import timezone
import pytz
from disty.models import Role, User, File, Url

# Create your tests here.


class ModelsTestCase(TestCase):
    def setUp(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        Role.objects.create(role_name="admin")
        User.objects.create(
            name="admin_user", password="password", role=Role.objects.get(pk=1)
        )
        File.objects.create(
            name="myfile.txt",
            checksum="sjhskjdhskjdhksajd",
            storage_location="local",
            path="/local/some/path",
            origin="internal",
            password="my_password",
            created_at=timezone.now(),
            owner=User.objects.get(pk=1),
        )

        Url.objects.create(
            expiry=tomorrow,
            download_count=0,
            url="http://some/link/url",
            created_at=timezone.now(),
            owner=User.objects.get(pk=1),
            file=File.objects.get(pk=1),
        )

    def test_create(self):
        admin = Role.objects.get(role_name="admin")
        assert admin.role_name == "admin"

    def test_create(self):
        admin = User.objects.get(name="admin_user")
        assert admin.role_id == 1
