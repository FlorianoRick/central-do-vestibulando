from django.urls import path

from . import views

app_name = "admissions"

urlpatterns = [
    path("", views.exam_list, name="list"),
    path("comparar/", views.exam_compare, name="compare"),
    path("provas/", views.paper_list, name="papers"),
    path("gabaritos/", views.paper_list, {"area": "gabaritos"}, name="answer_keys"),
    path("acervo/<int:pk>/download/", views.archive_document_download, name="archive_download"),
    path("<slug:slug>/", views.exam_detail, name="detail"),
]
