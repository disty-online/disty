import datetime
import os
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from disty.models import File, DownloadUrl, Access, UploadUrl
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from disty.forms import (
    FileForm,
    UploadUrlForm,
    DownloadUrlForm,
    EditDownloadUrlForm,
    EditUploadUrlForm,
)
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


@login_required
def home(request):
    user = User.objects.get(username=request.user)
    urls = DownloadUrl.objects.filter(owner=user.id)
    upload_urls = UploadUrl.objects.filter(owner=user.id)
    output_link = request.build_absolute_uri() + "upload/"
    return render(
        request,
        "disty/home.html",
        {
            "urls": urls,
            "user": user,
            "upload_urls": upload_urls,
            "output_link": output_link,
        },
    )


@login_required
def new_url(request):
    """
        Creates a url for file upload from external users.
    """
    user = User.objects.get(username=request.user)
    if request.method == "POST":
        form = UploadUrlForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.created_at = timezone.now()
            url.owner = user
            if url.description == "internal":
                # TODO: Add proper handling
                raise Exception
            url.save()
            output_link = request.build_absolute_uri().replace(
                "new_url/", f"upload/{str(url)}"
            )
            return render(
                request,
                "disty/new_url.html",
                {"url": url, "user": user, "path": output_link},
            )
    else:
        form = UploadUrlForm()
    return render(request, "disty/new_url.html", {"form": form})


@login_required
def edit_upload_url(request, url):
    """
        Allows existing URLs to be edited.
    """
    my_url = get_object_or_404(UploadUrl, url=url)
    user = User.objects.get(username=request.user)
    if request.method == "POST":
        url_form = EditUploadUrlForm(request.POST, instance=my_url)
        if url_form.is_valid():
            url = url_form.save(commit=False)
            if url.description == "internal":
                # TODO: Add proper handling
                raise Exception
            url.save()
            output_link = request.build_absolute_uri().replace(
                f"edit_upload_url/form/{str(url)}", f"upload/{str(url)}"
            )
            return render(
                request,
                "disty/new_url.html",
                {"url": url, "user": user, "path": output_link},
            )
    else:
        test_url = UploadUrl.objects.get(url=url)
        url_form = EditUploadUrlForm(instance=test_url)
    return render(request, "disty/new_url.html", {"form": url_form},)


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
    now = timezone.now()
    if request.method == "POST":
        file_form = FileForm(request.POST, request.FILES)
        url_form = DownloadUrlForm(request.POST)
        if file_form.is_valid() and url_form.is_valid():
            file = file_form.save(commit=False)
            file.owner = owner
            file.created_at = now
            file.name = file.document.name
            file.storage_location = "local"
            file.origin = "internal"
            file.save()
            url = url_form.save(commit=False)
            url.created_at = now
            url.owner = owner
            url.file = file
            url.save()
            return redirect("home")
    else:
        file_form = FileForm()
        url_form = DownloadUrlForm()
    return render(
        request,
        "disty/model_form_upload.html",
        {"file_form": file_form, "url_form": url_form},
    )


@login_required
def edit_upload(request, url):
    """
        Allows existing URLs to be edited.
    """
    my_url = get_object_or_404(DownloadUrl, url=url)
    if request.method == "POST":
        url_form = EditDownloadUrlForm(request.POST, instance=my_url)
        if url_form.is_valid():
            url = url_form.save(commit=True)
            return redirect("home")
    else:
        test_url = DownloadUrl.objects.get(url=url)
        url_form = EditDownloadUrlForm(instance=test_url)
    return render(request, "disty/model_form_upload.html", {"url_form": url_form},)


def upload(request, ruuid):
    """
        Allows file upload for external users.
    """
    if not ruuid:
        raise PermissionDenied
    now = timezone.now()
    url = UploadUrl.objects.get(url=ruuid)
    if url.expiry < now:
        raise PermissionDenied
    owner = url.owner
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.owner = owner
            file.created_at = now
            file.name = file.document.name
            file.storage_location = "local"
            file.origin = url.description
            file.save()
            url = DownloadUrl(created_at=now, owner=owner, file=file)
            url.save()
            return redirect("home")
    else:
        form = FileForm()
    return render(request, "disty/model_form_upload.html", {"file_form": form})


def download(request, uuid):
    """
        Download view for all public files.
    """
    if not uuid:
        raise PermissionDenied
    url = DownloadUrl.objects.get(url=uuid)
    user = request.user
    if url.owner != user and url.expiry < timezone.now():
        raise PermissionDenied
    if not url.download_limit:
        raise PermissionDenied
    file = File.objects.get(name=url.file.name)
    if all([file.origin == "external", str(user) == "AnonymousUser"]):
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
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                url.file.document.path
            )
            if url.owner != user:
                url.download_limit -= 1
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
