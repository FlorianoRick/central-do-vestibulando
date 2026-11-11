from django.urls import path

from . import views

app_name = "admissions"

urlpatterns = [
    path("", views.exam_list, name="list"),
    path("comparar/", views.exam_compare, name="compare"),
    path("instituicoes/", views.institution_list, name="institutions"),
    path("calendario/", views.calendar, name="calendar"),
    path("calendario/arquivo.ics", views.calendar_ics, name="calendar_ics"),
    path("provas/", views.paper_list, name="papers"),
    path("gabaritos/", views.paper_list, {"area": "gabaritos"}, name="answer_keys"),
    path("<slug:slug>/", views.exam_detail, name="detail"),
]
