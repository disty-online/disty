from django import forms
from disty.models import File


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = (
            "description",
            "document",
        )
