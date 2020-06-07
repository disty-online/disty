import datetime
from django.test import TestCase
from django.utils import timezone
import pytz
import pytest
from disty.models import Role, User, File, Url
import uuid
from unittest.mock import patch

# Create your tests here.


class ModelsTestCase(TestCase):
    @patch.object(uuid, "uuid4", return_value="my_unique_id")
    @pytest.mark.freeze_time("2020-01-01")
    def setUp(self, mock_uuid):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        Role.objects.create(role_name="admin")
        User.objects.create(
            name="admin_user", password="password", role=Role.objects.get(pk=1)
        )
        File.objects.create(
            name="myfile.txt",
            checksum="sjhskjdhskjdhksajd",
            storage_location="local",
            path="my_dir/some/path",
            origin="internal",
            password="my_password",
            created_at=timezone.now(),
            owner=User.objects.get(pk=1),
        )

        url = Url.objects.create(
            expiry=tomorrow,
            download_count=0,
            created_at=timezone.now(),
            owner=User.objects.get(pk=1),
            file=File.objects.get(pk=1),
        )
        url.url = url.generate_url()
        url.save()

    def test_create_user(self):
        admin = User.objects.get(name="admin_user")
        assert str(admin.role) == "admin"

    @pytest.mark.freeze_time("2020-01-01")
    def test_url(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        my_url = Url.objects.get(pk=1)
        assert my_url.download_count == 0
        assert str(my_url.owner) == "admin_user"
        assert str(my_url.file) == "local/my_dir/some/path/myfile.txt"
        assert my_url.expiry == tomorrow
        assert my_url.created_at == timezone.now()
        assert str(my_url) == "http://localhost/file/my_unique_id"
