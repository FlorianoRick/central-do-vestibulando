from django.contrib import messages
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from apps.admissions.models import ExamArchiveDocument, EntranceExam, Institution
from apps.news.models import NewsArticle
from apps.studies.models import StudyMaterial, StudyResource, StudySubject

from .forms import UserRoleForm


def _is_active_staff(user):
    return user.is_authenticated and user.is_active and user.is_staff


def _is_active_superuser(user):
    return user.is_authenticated and user.is_active and user.is_superuser


@user_passes_test(_is_active_staff, login_url="accounts:login")
def dashboard(request):
    content_links = [
        {
            "label": "Instituições",
            "url": reverse("admin:admissions_institution_changelist"),
            "count": Institution.objects.count(),
            "show_count": True,
        },
        {
            "label": "Vestibulares e processos",
            "url": reverse("admin:admissions_entranceexam_changelist"),
            "count": EntranceExam.objects.count(),
            "show_count": True,
        },
        {
            "label": "Acervo de provas",
            "url": reverse("admin:admissions_examarchivedocument_changelist"),
            "count": ExamArchiveDocument.objects.count(),
            "show_count": True,
        },
        {
            "label": "Matérias e recursos",
            "url": reverse("admin:studies_studysubject_changelist"),
            "count": StudySubject.objects.filter(is_active=True).count(),
            "secondary_count": StudyResource.objects.filter(is_published=True).count(),
            "show_count": True,
        },
        {
            "label": "Materiais de estudo",
            "url": reverse("admin:studies_studymaterial_changelist"),
            "count": StudyMaterial.objects.count(),
            "show_count": True,
        },
        {
            "label": "Notícias e avisos",
            "url": reverse("admin:news_newsarticle_changelist"),
            "count": NewsArticle.objects.count(),
            "show_count": True,
        },
        {
            "label": "Personalização do site",
            "url": reverse("appearance:editor"),
            "count": None,
            "show_count": False,
        },
    ]
    return render(
        request,
        "administration/dashboard.html",
        {
            "content_links": content_links,
            "pending_news": NewsArticle.objects.filter(
                is_published=True,
                is_demo=False,
                review_status=NewsArticle.ReviewStatus.PENDING,
            ).count(),
            "can_manage_users": request.user.is_superuser,
        },
    )


@user_passes_test(_is_active_superuser, login_url="accounts:login")
@require_http_methods(["GET", "POST"])
def user_roles(request):
    User = get_user_model()
    if request.method == "POST":
        with transaction.atomic():
            list(
                User.objects.select_for_update()
                .filter(is_active=True, is_superuser=True)
                .values_list("pk", flat=True)
            )
            target = get_object_or_404(
                User.objects.select_for_update(),
                pk=request.POST.get("user_id"),
            )
            form = UserRoleForm(request.POST, instance=target, actor=request.user)
            if form.is_valid():
                changed_fields = form.changed_data
                if changed_fields:
                    updated_user = form.save()
                    LogEntry.objects.create(
                        user=request.user,
                        content_type=ContentType.objects.get_for_model(User),
                        object_id=str(updated_user.pk),
                        object_repr=str(updated_user),
                        action_flag=CHANGE,
                        change_message=(
                            "Papéis alterados no painel de gestão: "
                            + ", ".join(changed_fields)
                        ),
                    )
                    messages.success(request, "Permissões atualizadas.")
                else:
                    messages.info(request, "Nenhuma alteração foi feita.")
                return redirect("administration:user_roles")
            messages.error(
                request,
                "Revise as permissões: "
                + "; ".join(
                    str(error)
                    for errors in form.errors.values()
                    for error in errors
                )
            )
    else:
        form = None

    users = User.objects.order_by("username")
    return render(
        request,
        "administration/user_roles.html",
        {"users": users, "role_form": form},
    )
