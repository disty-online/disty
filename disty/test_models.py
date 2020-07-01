from disty.models import UploadUrl, File, DownloadUrl
from django.contrib.auth.models import AnonymousUser, User
from django.utils import timezone
from django.test import RequestFactory, TestCase, client
from django.core.files import File as DjangoFile

class ModelTest(TestCase):
    def test_file_delete(self):
        user = User.objects.create_user(
                username="tester", email="tester@testing.com", password="mypassword"
        )
        file = File(
            name="hello.txt",
            description="hello.txt",
            origin="internal",
            created_at=timezone.now(),
            owner=user,
        )
        file.document = DjangoFile(open("disty/test_data/hello.txt"))
        file.save()
        file.delete()
