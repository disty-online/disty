from django.db import models


class Role(models.Model):
    role_name = models.CharField(max_length=50)

    def __str__(self):
        return self.role_name


class User(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    checksum = models.CharField(max_length=150)
    storage_location = models.CharField(max_length=100)
    path = models.CharField(max_length=256)
    origin = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField("created at")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Url(models.Model):
    expiry = models.DateTimeField("created at")
    download_count = models.IntegerField(default=0)
    url = models.CharField(max_length=250)
    created_at = models.DateTimeField("created at")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
