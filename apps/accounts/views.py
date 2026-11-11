from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.admissions.models import CalendarEvent, EntranceExam
from apps.studies.models import StudyPlan, StudySession
from .forms import EmailForm, EmailLoginForm, PreferencesForm, ProfileForm, RegistrationForm
from .models import FavoriteCalendarEvent, FavoriteExam, Notification, SavedMaterial

User = get_user_model()


class StudentLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get("remember"):
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            self.request.session.set_expiry(0)
        return response


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:account")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Conta criada. Agora você já pode entrar.")
        return redirect("accounts:login")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def account(request):
    profile_form = ProfileForm(instance=request.user.profile)
    email_form = EmailForm(instance=request.user)
    preferences_form = PreferencesForm(instance=request.user.preferences)

    if request.method == "POST":
        section = request.POST.get("section")
        if section == "profile":
            profile_form = ProfileForm(request.POST, instance=request.user.profile)
            email_form = EmailForm(request.POST, instance=request.user)
            if profile_form.is_valid() and email_form.is_valid():
                profile_form.save()
                email_form.save()
                messages.success(request, "Seus dados foram atualizados.")
                return redirect("accounts:account")
        elif section == "preferences":
            preferences_form = PreferencesForm(request.POST, instance=request.user.preferences)
            if preferences_form.is_valid():
                preferences_form.save()
                messages.success(request, "Suas preferências foram salvas.")
                return redirect("accounts:account")

    context = {
        "profile_form": profile_form,
        "email_form": email_form,
        "preferences_form": preferences_form,
        "favorite_exams": FavoriteExam.objects.filter(user=request.user).select_related("exam", "exam__institution"),
        "saved_materials": SavedMaterial.objects.filter(user=request.user).select_related("material", "material__subject"),
        "plans": StudyPlan.objects.filter(user=request.user, is_active=True),
        "notifications": Notification.objects.filter(user=request.user)[:6],
        "unread_count": Notification.objects.filter(user=request.user, read_at__isnull=True).count(),
        "sessions": StudySession.objects.filter(plan__user=request.user).select_related("subject", "plan")[:8],
    }
    return render(request, "accounts/account.html", context)


@login_required
@require_POST
def toggle_exam_favorite(request, exam_id):
    exam = get_object_or_404(EntranceExam, pk=exam_id, is_active=True)
    favorite, created = FavoriteExam.objects.get_or_create(user=request.user, exam=exam)
    if not created:
        favorite.delete()
        messages.info(request, "Vestibular removido dos salvos.")
    else:
        messages.success(request, "Vestibular salvo na sua conta.")
    return redirect("admissions:detail", slug=exam.slug)


@login_required
@require_POST
def toggle_event_favorite(request, event_id):
    event = get_object_or_404(CalendarEvent, pk=event_id)
    favorite, created = FavoriteCalendarEvent.objects.get_or_create(user=request.user, event=event)
    if not created:
        favorite.delete()
    messages.success(request, "Evento atualizado na sua lista de favoritos.")
    return redirect("admissions:calendar")


@login_required
@require_POST
def toggle_material_saved(request, material_id):
    from apps.studies.models import StudyMaterial

    material = get_object_or_404(StudyMaterial, pk=material_id, is_published=True)
    saved, created = SavedMaterial.objects.get_or_create(user=request.user, material=material)
    if not created:
        saved.delete()
        messages.info(request, "Material removido dos salvos.")
    else:
        messages.success(request, "Material salvo na sua conta.")
    return redirect("studies:detail", slug=material.slug)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
    return redirect("accounts:account")


@login_required
def change_password(request):
    return PasswordChangeView.as_view(
        template_name="accounts/password_change.html",
        success_url=reverse_lazy("accounts:account"),
    )(request)


@login_required
@require_POST
def delete_account(request):
    password = request.POST.get("password", "")
    confirmation = request.POST.get("confirmation", "")
    if not request.user.check_password(password):
        messages.error(request, "A senha informada não confere.")
        return redirect("accounts:account")
    if confirmation != request.user.get_username():
        messages.error(request, "Digite seu nome de usuário para confirmar a exclusão.")
        return redirect("accounts:account")
    request.user.delete()
    messages.success(request, "Sua conta e os dados associados foram excluídos.")
    return redirect("core:home")
