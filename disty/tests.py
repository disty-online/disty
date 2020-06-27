import datetime
import uuid
import os
from unittest import mock
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File as DjangoFile
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import Http404
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase, client
import pytest
from disty.views import (
    home,
    new_url,
    edit_upload,
    edit_upload_url,
    access,
    model_form_upload,
    download,
)
from disty.forms import (
    UploadUrlForm,
    EditUploadUrlForm,
    FileForm,
    DownloadUrlForm,
    EditDownloadUrlForm,
)
from disty.models import UploadUrl, File, DownloadUrl


class ViewTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="tester", email="tester@testing.com", password="mypassword"
        )
        self.client = client.Client()

    def test_home_anonymous(self):
        request = self.factory.get("/disty/")
        request.user = AnonymousUser()
        response = home(request)
        self.assertEqual(response.status_code, 302)

    def test_home_authenticated(self):
        request = self.factory.get("/disty/")
        request.user = self.user
        response = home(request)
        self.assertEqual(response.status_code, 200)

    def test_new_url_anonymous(self):
        request = self.factory.get("/disty/new_url/")
        request.user = AnonymousUser()
        response = home(request)
        self.assertEqual(response.status_code, 302)

    def test_new_url_get(self):
        request = self.factory.get("/disty/new_url/")
        request.user = self.user
        response = new_url(request)
        self.assertEqual(response.status_code, 200)

    @pytest.mark.freeze_time("2020-01-01")
    def test_new_url_post(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        form_data = {"description": "something", "expiry": tomorrow}
        my_form = UploadUrlForm(data=form_data)
        self.assertTrue(my_form.is_valid())
        with mock.patch("disty.views.UploadUrlForm") as Form:
            Form.return_value = my_form
            request = self.factory.post("/disty/new_url/", form=my_form)
            request.user = self.user
            response = new_url(request)
            self.assertEqual(response.status_code, 200)

    def test_edit_upload_url_anonymous(self):
        request = self.factory.get("/disty/edit_upload_url/form/")
        request.user = AnonymousUser()
        response = edit_upload(request, url=uuid.uuid4())
        self.assertEqual(response.status_code, 302)

    @pytest.mark.freeze_time("2020-01-01")
    def test_edit_upload_url_404(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        request = self.factory.get("/disty/edit_upload_url/form/")
        request.user = self.user
        with self.assertRaises(Http404):
            response = edit_upload_url(request, url=uuid.uuid4())
            self.assertEqual(response.status_code, 404)

    @pytest.mark.freeze_time("2020-01-01")
    def test_edit_upload_url_200(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        upload_url = UploadUrl(
            expiry=tomorrow,
            owner=self.user,
            description="description",
            created_at=timezone.now(),
        )
        upload_url.save()
        request = self.factory.get("/disty/edit_upload_url/form/")
        request.user = self.user
        response = edit_upload_url(request, url=upload_url.url)
        self.assertEqual(response.status_code, 200)

    @pytest.mark.freeze_time("2020-01-01")
    def test_edit_upload_url_post(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        upload_url = UploadUrl(
            expiry=tomorrow,
            owner=self.user,
            description="description",
            created_at=timezone.now(),
        )
        upload_url.save()
        form_data = {
            "description": "something",
            "expiry": tomorrow,
        }
        my_form = EditUploadUrlForm(data=form_data, instance=upload_url)
        self.assertTrue(my_form.is_valid())
        with mock.patch("disty.views.EditUploadUrlForm") as Form:
            Form.return_value = my_form
            request = self.factory.post("/disty/edit_upload_url/form/", form=my_form)
            request.user = self.user
            response = edit_upload_url(request, url=upload_url.url)
            self.assertEqual(response.status_code, 200)

    def test_access_anonymous(self):
        request = self.factory.get("/disty/access/")
        request.user = AnonymousUser()
        response = access(request)
        self.assertEqual(response.status_code, 302)

    def test_access_get(self):
        request = self.factory.get("/disty/access/")
        request.user = self.user
        response = access(request)
        self.assertEqual(response.status_code, 200)

    def test_model_form_upload_anonymous(self):
        request = self.factory.get("/disty/uploads/form/")
        request.user = AnonymousUser()
        response = model_form_upload(request)
        self.assertEqual(response.status_code, 302)

    def test_model_form_upload_get(self):
        request = self.factory.get("/disty/uploads/form/")
        request.user = self.user
        response = model_form_upload(request)
        self.assertEqual(response.status_code, 200)

    def test_model_form_upload_post(self):
        # TODO
        pass

    def test_edit_upload_anonymous(self):
        request = self.factory.get("/disty/edit_upload/form/")
        request.user = AnonymousUser()
        response = edit_upload(request)
        self.assertEqual(response.status_code, 302)

    @pytest.mark.freeze_time("2020-01-01")
    def test_edit_upload_get(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        my_file = File(
            name="django.png",
            description="django.png",
            origin="internal",
            created_at=timezone.now(),
            owner=self.user,
        )
        my_file.document = DjangoFile(open("disty/test_data/hello.txt"))
        my_file.save()
        download_url = DownloadUrl(
            expiry=tomorrow,
            download_limit=10,
            created_at=timezone.now(),
            owner=self.user,
            file=my_file,
        )
        download_url.save()
        request = self.factory.get("/disty/edit_upload/form/")
        request.user = self.user
        response = edit_upload(request, url=download_url.url)
        self.assertEqual(response.status_code, 200)

    @pytest.mark.freeze_time("2020-01-01")
    def test_edit_upload_post(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        my_file = File(
            name="django.png",
            description="django.png",
            origin="internal",
            created_at=timezone.now(),
            owner=self.user,
        )
        my_file.document = DjangoFile(open("disty/test_data/hello.txt"))
        my_file.save()
        download_url = DownloadUrl(
            expiry=tomorrow,
            download_limit=10,
            created_at=timezone.now(),
            owner=self.user,
            file=my_file,
        )
        download_url.save()
        form_data = {"expiry": tomorrow, "download_limit": 20}
        my_form = EditDownloadUrlForm(data=form_data, instance=download_url)
        self.assertTrue(my_form.is_valid())
        with mock.patch("disty.views.EditDownloadUrlForm") as Form:
            Form.return_value = my_form
            request = self.factory.post("/disty/edit_upload/form/")
            request.user = self.user
            response = edit_upload(request, url=download_url.url)
            self.assertEqual(response.status_code, 302)

    def test_download_ok(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        my_file = File(
            name="django.png",
            description="django.png",
            origin="internal",
            created_at=timezone.now(),
            owner=self.user,
        )
        my_file.document = DjangoFile(open("disty/test_data/hello.txt"))
        my_file.save()
        download_url = DownloadUrl(
            expiry=tomorrow,
            download_limit=10,
            created_at=timezone.now(),
            owner=self.user,
            file=my_file,
        )
        download_url.save()
        request = self.factory.post("/disty/download/")
        request.user = AnonymousUser()
        response = download(request, uuid=download_url.url)
        self.assertEqual(response.status_code, 200)

    def test_download_invalid(self):
        request = self.factory.post("/disty/download/")
        with self.assertRaises(Http404):
            request.user = AnonymousUser()
            response = download(request, uuid=uuid.uuid4())
            self.assertEqual(response.status_code, 404)

    def test_download_no_uuid(self):
        request = self.factory.post("/disty/download/")
        with self.assertRaises(PermissionDenied):
            request.user = AnonymousUser()
            response = download(request, uuid="")
            self.assertEqual(response.status_code, 403)

    def test_download_nok_external_anonymous(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        my_file = File(
            name="django.png",
            description="django.png",
            origin="xpto",
            created_at=timezone.now(),
            owner=self.user,
        )
        my_file.document = DjangoFile(open("disty/test_data/hello.txt"))
        my_file.save()
        download_url = DownloadUrl(
            expiry=tomorrow,
            download_limit=10,
            created_at=timezone.now(),
            owner=self.user,
            file=my_file,
        )
        download_url.save()
        request = self.factory.post("/disty/download/")
        with self.assertRaises(PermissionDenied):
            request.user = AnonymousUser()
            response = download(request, uuid=download_url.url)
            self.assertEqual(response.status_code, 403)

    def test_download_nok_limit(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        my_file = File(
            name="django.png",
            description="django.png",
            origin="internal",
            created_at=timezone.now(),
            owner=self.user,
        )
        my_file.document = DjangoFile(open("disty/test_data/hello.txt"))
        my_file.save()
        download_url = DownloadUrl(
            expiry=tomorrow,
            download_limit=0,
            created_at=timezone.now(),
            owner=self.user,
            file=my_file,
        )
        download_url.save()
        request = self.factory.post("/disty/download/")
        with self.assertRaises(PermissionDenied):
            request.user = AnonymousUser()
            response = download(request, uuid=download_url.url)
            self.assertEqual(response.status_code, 403)

    def test_download_nok_expired(self):
        tomorrow = timezone.now() + datetime.timedelta(days=-1)
        my_file = File(
            name="django.png",
            description="django.png",
            origin="internal",
            created_at=timezone.now(),
            owner=self.user,
        )
        my_file.document = DjangoFile(open("disty/test_data/hello.txt"))
        my_file.save()
        download_url = DownloadUrl(
            expiry=tomorrow,
            download_limit=0,
            created_at=timezone.now(),
            owner=self.user,
            file=my_file,
        )
        download_url.save()
        request = self.factory.post("/disty/download/")
        with self.assertRaises(PermissionDenied):
            request.user = AnonymousUser()
            response = download(request, uuid=download_url.url)
            self.assertEqual(response.status_code, 403)
