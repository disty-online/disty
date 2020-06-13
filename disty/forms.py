from django import forms
from disty.models import File, UploadUrl


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = (
            "description",
            "document",
        )


class UploadUrlForm(forms.ModelForm):
    class Meta:
        model = UploadUrl
        fields = ("description",)
