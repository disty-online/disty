from django import forms
from disty.models import File, UploadUrl, DownloadUrl


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ("description", "document")


class DownloadUrlForm(forms.ModelForm):
    class Meta:
        model = DownloadUrl
        fields = ("download_limit",)


class UploadUrlForm(forms.ModelForm):
    class Meta:
        model = UploadUrl
        fields = ("description",)
