from django.urls import include, path
from disty import views

urlpatterns = [path("", views.hello)]
