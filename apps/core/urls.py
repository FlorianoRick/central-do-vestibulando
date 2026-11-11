from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("privacidade/", views.privacy, name="privacy"),
    path("termos/", views.terms, name="terms"),
]
