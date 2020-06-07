import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from disty.models import User, File, Url
from django.http import HttpResponse
from disty.forms import FileForm
from django.utils import timezone


def hello(request):
    return HttpResponse("hello")


def home(request):
    files = File.objects.all()
    return render(request, "disty/home.html", {"files": files})


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
            file.save()
            url = Url(expiry=tomorrow, created_at=now, owner=owner, file=file)
            url.save()
            return redirect("home")
    else:
        form = FileForm()
    return render(request, "disty/model_form_upload.html", {"form": form})
