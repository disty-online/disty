import datetime
import os
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from disty.models import File, DownloadUrl, Access, UploadUrl
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from disty.forms import FileForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def home(request):
    user = User.objects.get(username=request.user)
    urls = DownloadUrl.objects.filter(owner=user.id)
    return render(request, "disty/home.html", {"urls": urls, "user": user})


@login_required
def access(request):
    """
        Displays all access history on files for specific user.
    """
    user = User.objects.get(username=request.user)
    urls = DownloadUrl.objects.filter(owner=user.id)
    ids = [url.id for url in urls]
    accesses = Access.objects.filter(url__in=ids)
    return render(
        request, "disty/access.html", {"urls": urls, "user": user, "accesses": accesses}
    )


@login_required
def model_form_upload(request):
    """
        Allows file upload for internal users.
    """
    owner = request.user
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
            url = DownloadUrl(expiry=tomorrow, created_at=now, owner=owner, file=file)
            url.save()
            return redirect("home")
    else:
        form = FileForm()
    return render(request, "disty/model_form_upload.html", {"form": form})


def upload(request, ruuid):
    """
        Allows file upload for external users.
    """
    if not ruuid:
        raise PermissionDenied
    url = UploadUrl.objects.get(url=ruuid)
    if url.expiry < timezone.now():
        raise PermissionDenied
    owner = url.owner
    tomorrow = timezone.now() + datetime.timedelta(days=1)
    now = timezone.now()
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.owner = owner
            file.created_at = now
            file.name = file.document.name
            file.origin = "external"
            file.save()
            url = DownloadUrl(expiry=tomorrow, created_at=now, owner=owner, file=file)
            url.save()
            return redirect("home")
    else:
        form = FileForm()
    return render(request, "disty/model_form_upload.html", {"form": form})


def download(request, uuid):
    """
        Download view for all public files.
    """
    if not uuid:
        raise PermissionDenied
    url = DownloadUrl.objects.get(url=uuid)
    if url.expiry < timezone.now():
        raise PermissionDenied
    file = File.objects.get(name=url.file.name)
    if all([file.origin == "external", str(request.user) == "AnonymousUser"]):
        raise PermissionDenied
    Access(
        source_ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        timestamp=timezone.now(),
        file=File.objects.get(name=file.name),
        url=url,
        user=url.owner,
    ).save()
    if os.path.exists(url.file.document.path):
        with open(url.file.document.path, "rb") as fh:
            # TODO: Update content_type
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                url.file.document.path
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
