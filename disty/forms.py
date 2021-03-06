from django import forms
from disty.models import File, UploadUrl, DownloadUrl
from disty.settings import DEFAULT_DOWNLOAD_EXPIRY_DAYS, DEFAULT_UPLOAD_URL_EXPIRY_DAYS
import datetime
from django.utils import timezone


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ("description", "document")


class DownloadUrlForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DownloadUrlForm, self).__init__(*args, **kwargs)
        default_expiry = timezone.now() + datetime.timedelta(
            days=DEFAULT_DOWNLOAD_EXPIRY_DAYS
        )
        self.fields["expiry"].initial = default_expiry

    class Meta:
        model = DownloadUrl
        fields = ("download_limit", "expiry")


class EditDownloadUrlForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditDownloadUrlForm, self).__init__(*args, **kwargs)
        instance = kwargs["instance"]
        self.fields["expiry"].initial = instance.expiry

    class Meta:
        model = DownloadUrl
        fields = ("download_limit", "expiry")


class UploadUrlForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UploadUrlForm, self).__init__(*args, **kwargs)
        default_expiry = timezone.now() + datetime.timedelta(
            days=DEFAULT_UPLOAD_URL_EXPIRY_DAYS
        )
        self.fields["expiry"].initial = default_expiry

    class Meta:
        model = UploadUrl
        fields = ("description", "expiry")


class EditUploadUrlForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditUploadUrlForm, self).__init__(*args, **kwargs)
        instance = kwargs["instance"]
        self.fields["expiry"].initial = instance.expiry

    class Meta:
        model = UploadUrl
        fields = (
            "description",
            "expiry",
        )
