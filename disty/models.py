import uuid
from django.db import models


class Role(models.Model):
    role_name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.role_name)


class User(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class File(models.Model):
    document = models.FileField(upload_to="documents/")
    name = models.CharField(max_length=100, db_index=True)
    description = models.CharField(max_length=255, blank=True)
    checksum = models.CharField(max_length=150)
    storage_location = models.CharField(max_length=100)
    path = models.CharField(max_length=256)
    origin = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)
        # return "/".join([self.storage_location, self.path, self.name])


class Url(models.Model):
    expiry = models.DateTimeField("expiry at")
    download_count = models.IntegerField(default=0)
    url = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField("created at")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)

    def __str__(self):
        base_url = "http://localhost/file/"
        return f"{base_url}{self.url}"


class Access(models.Model):
    source_ip = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=1000)
    timestamp = models.DateTimeField("timestamp")
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.ForeignKey(Url, on_delete=models.CASCADE)

    def __str__(self):
        return self.file.name
