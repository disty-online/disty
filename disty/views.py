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
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    urls = Url.objects.all()
    return render(request, "disty/home.html", {"files": urls})


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
    Access(
        source_ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        timestamp=timezone.now(),
        file=File.objects.get(name=file),
        url=url,
        user=url.owner,
    ).save()

    file_path = os.path.join("documents", file)
    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            # TODO: Update content_type
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                file_path
            )
            url.download_count += 1
            url.save()
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
