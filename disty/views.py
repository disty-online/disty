import datetime
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from disty.models import File, DownloadUrl, Access, UploadUrl
from disty.settings import DEFAULT_DOWNLOAD_EXPIRY_DAYS, logger
from disty import __version__
from disty.forms import (
    FileForm,
    UploadUrlForm,
    DownloadUrlForm,
    EditDownloadUrlForm,
    EditUploadUrlForm,
)


@login_required
def home(request):
    now = timezone.now()
    user = User.objects.get(username=request.user)
    urls = DownloadUrl.objects.filter(owner=user.id)
    upload_urls = UploadUrl.objects.filter(owner=user.id)
    external_file_urls = []
    internal_file_urls = []

    for url in urls:
        if url.file.origin == "internal":
            internal_file_urls.append(url)
        else:
            external_file_urls.append(url)

    available_downloads = 0
    for file in internal_file_urls:
        if file.expiry > now and file.download_limit > 0:
            available_downloads += 1

    available_links = 0
    for link in upload_urls:
        if link.expiry > now:
            available_links += 1

    return render(
        request,
        "disty/home.html",
        {
            "user": user,
            "external": external_file_urls,
            "internal": internal_file_urls,
            "available_downloads": available_downloads,
            "available_links": available_links,
            "upload_urls": upload_urls,
            "version": __version__,
        },
    )


@login_required
def files_by_user(request):
    user = User.objects.get(username=request.user)
    urls = DownloadUrl.objects.filter(owner=user.id)
    internal_file_urls = []

    for url in urls:
        if url.file.origin == "internal":
            internal_file_urls.append(url)

    return render(
        request, "disty/files_by_user.html", {"user": user, "files": internal_file_urls}
    )


@login_required
def files_for_user(request):
    user = User.objects.get(username=request.user)
    urls = DownloadUrl.objects.filter(owner=user.id)
    external_file_urls = []

    for url in urls:
        if url.file.origin != "internal":
            external_file_urls.append(url)

    return render(
        request,
        "disty/files_for_user.html",
        {"user": user, "files": external_file_urls},
    )


@login_required
def links_by_user(request):
    user = User.objects.get(username=request.user)
    upload_urls = UploadUrl.objects.filter(owner=user.id)
    output_link = request.build_absolute_uri().replace("created_links/", f"upload/")

    return render(
        request,
        "disty/links_by_user.html",
        {"user": user, "upload_urls": upload_urls, "output_link": output_link,},
    )


@login_required
def new_url(request):
    """
        Creates a url for for external users so they can upload files.
    """
    user = User.objects.get(username=request.user)
    if request.method == "POST":
        form = UploadUrlForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.created_at = timezone.now()
            url.owner = user
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
        upload_url = UploadUrl.objects.get(url=url)
        url_form = EditUploadUrlForm(instance=upload_url)
    return render(request, "disty/new_url.html", {"form": url_form},)


@login_required
def access(request):
    """
        Displays all access history on files for specific user.
    """
    user = User.objects.get(username=request.user)
    urls = DownloadUrl.objects.filter(owner=user.id)
    ids = [url.id for url in urls if url.file.origin == "internal"]
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
        download_url = DownloadUrl.objects.get(url=url)
        url_form = EditDownloadUrlForm(instance=download_url)
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
            file.origin = url.url
            file.save()
            default_expiry = now + datetime.timedelta(days=DEFAULT_DOWNLOAD_EXPIRY_DAYS)
            url = DownloadUrl(
                created_at=now, owner=owner, expiry=default_expiry, file=file
            )
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
        logger.debug("UUID %s not found", uuid)
        raise PermissionDenied
    try:
        url = DownloadUrl.objects.get(url=uuid)
    except ObjectDoesNotExist:
        logger.debug("Unable to find download URL %s", uuid)
        raise Http404
    user = request.user
    if url.owner != user and url.expiry < timezone.now():
        logger.debug(
            "Tried to access url %s expiry %s with user %s", url, url.expiry, user
        )
        raise PermissionDenied
    if not url.download_limit:
        logger.info("Number of downloads exceeded for %s", url)
        raise PermissionDenied
    file = File.objects.get(pk=url.file.pk)
    if all([file.origin != "internal", str(user) == "AnonymousUser"]):
        logger.debug("Anonymous user tried to access externally generated file %s", url)
        raise PermissionDenied
    Access(
        source_ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        timestamp=timezone.now(),
        file=File.objects.get(pk=file.pk),
        url=url,
        user=url.owner,
    ).save()
    if os.path.exists(url.file.document.path):
        logger.debug("Found file %s", url.file.document.path)
        with open(url.file.document.path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(
                url.file.document.path
            )
            if url.owner != user:
                url.download_limit -= 1
            url.save()
            return response
    logger.error("Could not find file %s", url.file.document.path)
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
