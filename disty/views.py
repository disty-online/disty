import datetime
import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from disty.models import User, File, Url
from django.http import HttpResponse, Http404
from disty.forms import FileForm
from django.utils import timezone


def hello(request):
    return HttpResponse("hello")


def home(request):

    urls = Url.objects.all()
    return render(request, "disty/home.html", {"files": urls})


def simple_upload(request):
    if request.method == "POST" and request.FILES["myfile"]:
        myfile = request.FILES["myfile"]
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(
            request,
            "disty/simple_upload.html",
            {"uploaded_file_url": uploaded_file_url},
        )
    return render(request, "disty/simple_upload.html")


def model_form_upload(request):
    owner = User.objects.get(name="Pingo")
    tomorrow = timezone.now() + datetime.timedelta(days=1)
    now = timezone.now()
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.owner = owner
            file.created_at = now
            file.name = file.document.name
            file.save()
            url = Url(expiry=tomorrow, created_at=now, owner=owner, file=file)
            url.save()
            return redirect("home")
    else:
        form = FileForm()
    return render(request, "disty/model_form_upload.html", {"form": form})


def download(request, uuid):
    url = Url.objects.get(url=uuid)
    file = url.file.name
    file_path = os.path.join("documents", file)
    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                file_path
            )
            return response
    raise Http404
