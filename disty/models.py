import hashlib
import os
import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from disty.settings import DEFAULT_DOWNLOAD_LIMIT, UPLOAD_FOLDER, logger


class File(models.Model):
    document = models.FileField(upload_to=UPLOAD_FOLDER)
    name = models.CharField(max_length=100, db_index=True)
    description = models.CharField(max_length=255, blank=True)
    checksum = models.CharField(max_length=150)
    storage_location = models.CharField(max_length=100)
    path = models.CharField(max_length=256)
    origin = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)

    def save(self, *args, **kwargs):
        """
        Saves file on disc and generates a sha1sum.
        """
        super().save(*args, **kwargs)
        logger.debug("Saving file %s", self.document.path)
        checksum = hashlib.sha1()
        with open(self.document.path, "rb") as file:
            while True:
                data = file.read(65536)
                if not data:
                    break
                checksum.update(data)
        self.checksum = checksum.hexdigest()
        self.path = self.document.path
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.name)


class DownloadUrl(models.Model):
    expiry = models.DateTimeField("expiry at")
    download_limit = models.IntegerField(default=DEFAULT_DOWNLOAD_LIMIT)
    url = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField("created at")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    file = models.ForeignKey(File, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.url}"


class UploadUrl(models.Model):
    expiry = models.DateTimeField("expiry at")
    url = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField("created at")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.url}"


class Access(models.Model):
    source_ip = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=1000)
    timestamp = models.DateTimeField("timestamp")
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    url = models.ForeignKey(DownloadUrl, on_delete=models.CASCADE)

    def __str__(self):
        return self.file.name


@receiver(models.signals.post_delete, sender=File)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes physical files on `post_delete` """
    logger.debug("Deleting file %s", instance.document.path)
    if os.path.isfile(instance.document.path):
        os.remove(instance.document.path)
    else:
        logger.error("Unable to find file %s", instance.document.path)
