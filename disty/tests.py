import datetime
import uuid
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
import pytest
from disty.models import Role, User, File, Url, Access


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
        Access.objects.create(
            source_ip="192.168.0.1",
            user_agent="Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19",
            timestamp=timezone.now(),
            file=File.objects.get(pk=1),
            user=User.objects.get(pk=1),
            url=Url.objects.get(pk=1),
        )

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

    @pytest.mark.freeze_time("2020-01-01")
    def test_access(self):
        my_access = Access.objects.get(pk=1)
        assert str(my_access.file) == "local/my_dir/some/path/myfile.txt"
        assert str(my_access.user) == "admin_user"
        assert str(my_access.url) == "http://localhost/file/my_unique_id"
