from django.urls import include, path
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from disty import views

urlpatterns = [
    url(r"^$", views.home, name="home"),
    url(r"^access/", views.access, name="access"),
    url(r"^download/(?P<uuid>.*)$", views.download, name="download"),
    url(r"^logout/", views.logout_view, name="logout"),
    url(r"^uploads/form/$", views.model_form_upload, name="model_form_upload"),
    url(r"^upload/(?P<ruuid>.*)$", views.upload, name="upload"),
]
