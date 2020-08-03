from django.urls import path
from django.conf.urls import url
from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeView,
)
from disty import views


urlpatterns = [
    url(r"^$", views.home, name="home"),
    url(r"^user_uploaded/", views.files_by_user, name="files_by_user"),
    url(r"^external_files/", views.files_for_user, name="files_for_user"),
    url(r"^created_links/", views.links_by_user, name="links_by_user"),
    url(r"^access/", views.access, name="access"),
    url(r"^download/(?P<uuid>.*)$", views.download, name="download"),
    url(r"^edit_upload/form/(?P<url>.*)$", views.edit_upload, name="edit_upload"),
    url(
        r"^edit_upload_url/form/(?P<url>.*)$",
        views.edit_upload_url,
        name="edit_upload_url",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    url(r"^new_url/", views.new_url, name="new_url"),
    path("password_change/", PasswordChangeView.as_view(success_url="/disty")),
    url(r"^uploads/form/$", views.model_form_upload, name="model_form_upload"),
    url(r"^upload/(?P<ruuid>.*)$", views.upload, name="upload"),
]
