from django.urls import include, path
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from disty import views

urlpatterns = [
    url(r"^$", views.home, name="home"),
    url(r"^uploads/simple/$", views.simple_upload, name="simple_upload"),
    url(r"^uploads/form/$", views.model_form_upload, name="model_form_upload"),
    url(r"^download/(?P<uuid>.*)$", views.download, name="download"),
    url(r"^admin/", admin.site.urls),
]
