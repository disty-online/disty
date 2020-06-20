from django.urls import include, path
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from disty import views
from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
)


urlpatterns = [
    url(r"^$", views.home, name="home"),
    url(r"^access/", views.access, name="access"),
    url(r"^download/(?P<uuid>.*)$", views.download, name="download"),
    url(r"^edit_upload/form/(?P<url>.*)$", views.edit_upload, name="edit_upload"),
    path("logout/", LogoutView.as_view(), name="logout"),
    url(r"^new_url/", views.new_url, name="new_url"),
    path("password_change/", PasswordChangeView.as_view(success_url="/disty")),
    url(r"^uploads/form/$", views.model_form_upload, name="model_form_upload"),
    url(r"^upload/(?P<ruuid>.*)$", views.upload, name="upload"),
]
