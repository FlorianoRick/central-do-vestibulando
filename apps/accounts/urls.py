from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"

urlpatterns = [
    path("entrar/", views.StudentLoginView.as_view(), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("criar/", views.register, name="register"),
    path("minha-conta/", views.account, name="account"),
    path("senha/alterar/", views.change_password, name="password_change"),
    path("senha/recuperar/", auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html", email_template_name="accounts/password_reset_email.html", subject_template_name="accounts/password_reset_subject.txt", success_url=reverse_lazy("accounts:password_reset_done")), name="password_reset"),
    path("senha/recuperar/enviado/", auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path("senha/redefinir/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html", success_url=reverse_lazy("accounts:password_reset_complete")), name="password_reset_confirm"),
    path("senha/redefinida/", auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
    path("excluir/", views.delete_account, name="delete_account"),
    path("salvar-vestibular/<int:exam_id>/", views.toggle_exam_favorite, name="toggle_exam_favorite"),
    path("salvar-evento/<int:event_id>/", views.toggle_event_favorite, name="toggle_event_favorite"),
    path("salvar-material/<int:material_id>/", views.toggle_material_saved, name="toggle_material_saved"),
    path("aviso/<int:notification_id>/lido/", views.mark_notification_read, name="mark_notification_read"),
]
