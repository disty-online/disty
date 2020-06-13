from django import forms
from disty.models import File, UploadUrl, DownloadUrl
import datetime
from django.utils import timezone


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ("description", "document")


class DownloadUrlForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):

        super(DownloadUrlForm, self).__init__(*args, **kwargs)
        default_expiry = timezone.now() + datetime.timedelta(days=1)
        self.fields["expiry"].initial = default_expiry

    class Meta:
        model = DownloadUrl
        fields = ("download_limit", "expiry")


class UploadUrlForm(forms.ModelForm):
    class Meta:
        model = UploadUrl
        fields = ("description",)
