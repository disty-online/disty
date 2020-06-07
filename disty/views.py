import datetime
import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from disty.models import User, File, Url, Access
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
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
    if url.expiry < timezone.now():
        raise PermissionDenied
    file = url.file.name
    source_ip = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    access = Access(
        source_ip=source_ip,
        user_agent=user_agent,
        timestamp=timezone.now(),
        file=File.objects.get(name=url.file.name),
        url=url,
        user=url.owner,
    )
    access.save()

    file_path = os.path.join("documents", file)
    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            # TODO: Update content_type
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                file_path
            )
            return response
    raise Http404


def get_client_ip(request) -> str:
    """
        Finds the original IP address from the requester.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
