from django.urls import path

from . import views

app_name = "studies"

urlpatterns = [
    path("", views.material_list, name="list"),
    path("comparar-programas/", views.syllabus_compare, name="compare"),
    path("plano/", views.planner, name="planner"),
    path("planos/<int:plan_id>/editar/", views.edit_plan, name="edit_plan"),
    path("planos/<int:plan_id>/arquivar/", views.archive_plan, name="archive_plan"),
    path("planos/<int:plan_id>/", views.plan_detail, name="plan_detail"),
    path("planos/<int:plan_id>/sessoes/adicionar/", views.add_session, name="add_session"),
    path("planos/<int:plan_id>/sessoes/<int:session_id>/atualizar/", views.update_session, name="update_session"),
    path("simulados/adicionar/", views.add_mock_result, name="add_mock_result"),
    path("<slug:slug>/", views.material_detail, name="detail"),
]
