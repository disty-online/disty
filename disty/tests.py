import datetime
import uuid
from unittest.mock import patch
from django.test import TestCase, RequestFactory, Client
from django.utils import timezone
from django.urls import reverse
import pytest
from disty.models import File, DownloadUrl, Access
from django.core.files.uploadedfile import SimpleUploadedFile


class ModelsTestCase(TestCase):
    @pytest.mark.freeze_time("2020-01-01")
    def setUp(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        Role.objects.create(role_name="admin")
        User.objects.create(
            name="admin_user", password="password", role=Role.objects.get(pk=1)
        )
        File.objects.create(
            name="0001.sh",
            storage_location="local",
            path="my_dir/some/path",
            origin="internal",
            password="my_password",
            created_at=timezone.now(),
            owner=User.objects.get(pk=1),
        )

        url = DownloadUrl.objects.create(
            expiry=tomorrow,
            download_limit=0,
            created_at=timezone.now(),
            owner=User.objects.get(pk=1),
            file=File.objects.get(pk=1),
        )
        url.save()
        Access.objects.create(
            source_ip="192.168.0.1",
            user_agent="Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19",
            timestamp=timezone.now(),
            file=File.objects.get(pk=1),
            user=User.objects.get(pk=1),
            url=DownloadUrl.objects.get(pk=1),
        )

    def tearDown(self):
        File.objects.all().delete()

    def test_create_user(self):
        admin = User.objects.get(name="admin_user")
        assert str(admin.role) == "admin"

    @pytest.mark.freeze_time("2020-01-01")
    def test_url(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        my_url = DownloadUrl.objects.get(pk=1)
        assert my_url.download_limit == 0
        assert str(my_url.owner) == "admin_user"
        assert str(my_url.file) == "0001.sh"
        assert my_url.expiry == tomorrow
        assert my_url.created_at == timezone.now()

    @pytest.mark.freeze_time("2020-01-01")
    def test_access(self):
        my_access = Access.objects.get(pk=1)
        assert str(my_access.file) == "0001.sh"
        assert str(my_access.user) == "admin_user"


class ViewsTestCase(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_home(self):
        response = self.client.get(reverse("home"))
        assert response.status_code == 200
        self.assertContains(response, "Model Form Upload")
