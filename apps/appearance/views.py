from mimetypes import guess_type

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import SiteAppearanceForm
from .models import HOME_SECTION_CHOICES
from .services import (
    configuration_snapshot,
    get_active_appearance,
    record_configuration_change,
    remove_replaced_assets,
    restore_default_values,
)


def _editor_context(appearance, form):
    visibility = {
        "exam_overview": appearance.show_home_upcoming_exams or appearance.show_home_open_exams,
        "updates": appearance.show_home_results or appearance.show_home_news,
        "featured_exams": appearance.show_home_featured_exams,
        "materials": appearance.show_home_materials,
    }
    return {
        "appearance": appearance,
        "form": form,
        "home_section_choices": HOME_SECTION_CHOICES,
        "home_sections": [key for key in appearance.home_section_order if visibility.get(key, False)],
        "history": appearance.history.select_related("changed_by")[:10],
    }


@login_required
def editor(request):
    if not request.user.is_active or not (
        request.user.is_superuser
        or (request.user.is_staff and request.user.has_perm("appearance.change_siteappearance"))
    ):
        raise PermissionDenied

    appearance = get_active_appearance(request)
    if request.method == "POST" and request.POST.get("restore_defaults") == "1":
        previous = configuration_snapshot(appearance)
        old_assets = {name: getattr(appearance, name).name or "" for name in ("logo", "favicon")}
        draft_was_present = bool(appearance.draft_settings)
        restore_default_values(appearance)
        appearance.last_modified_by = request.user
        current = configuration_snapshot(appearance)
        if previous != current or draft_was_present:
            appearance.full_clean()
            with transaction.atomic():
                appearance.save()
                remove_replaced_assets(old_assets, appearance)
                record_configuration_change(appearance, request.user, previous, configuration_snapshot(appearance))
            messages.success(request, "A aparência original foi restaurada.")
        else:
            messages.info(request, "O site já está usando a aparência original.")
        return redirect("appearance:editor")

    previous_snapshot = configuration_snapshot(appearance)
    previous_assets = {name: getattr(appearance, name).name or "" for name in ("logo", "favicon")}
    initial = appearance.draft_settings if request.method == "GET" and appearance.draft_settings else None
    form = SiteAppearanceForm(
        request.POST or None,
        request.FILES or None,
        instance=appearance,
        initial=initial,
    )
    if request.method == "POST" and form.is_valid():
        updated_appearance = form.save(commit=False)
        if request.POST.get("save_draft") == "1":
            if request.FILES:
                form.add_error(None, "Publique as alterações para aplicar um novo logotipo ou ícone; arquivos não são armazenados em rascunhos.")
            else:
                snapshot = configuration_snapshot(updated_appearance)
                snapshot.pop("logo", None)
                snapshot.pop("favicon", None)
                appearance.draft_settings = snapshot
                appearance.draft_saved_at = timezone.now()
                appearance.draft_saved_by = request.user
                appearance.save(update_fields=("draft_settings", "draft_saved_at", "draft_saved_by"))
                messages.success(request, "Rascunho salvo. As alterações ainda não estão publicadas.")
                return redirect("appearance:editor")
        else:
            updated_appearance.last_modified_by = request.user
            updated_appearance.draft_settings = {}
            updated_appearance.draft_saved_at = None
            updated_appearance.draft_saved_by = None
            current = configuration_snapshot(updated_appearance)
            if previous_snapshot != current or request.FILES or appearance.draft_settings:
                updated_appearance.full_clean()
                with transaction.atomic():
                    updated_appearance.save()
                    form.save_m2m()
                    remove_replaced_assets(previous_assets, updated_appearance)
                    record_configuration_change(updated_appearance, request.user, previous_snapshot, configuration_snapshot(updated_appearance))
                messages.success(request, "As alterações foram publicadas.")
            else:
                messages.info(request, "Nenhuma alteração foi feita.")
            return redirect("appearance:editor")

    if request.method == "POST":
        appearance.refresh_from_db()
        request.site_appearance = appearance
    return render(request, "appearance/editor.html", _editor_context(appearance, form))


def asset(request, asset_name):
    if asset_name not in {"logo", "favicon"}:
        raise Http404
    appearance = get_active_appearance(request)
    image = getattr(appearance, asset_name)
    if not image:
        raise Http404
    try:
        image.open("rb")
    except (FileNotFoundError, OSError):
        raise Http404 from None
    response = FileResponse(image, content_type=guess_type(image.name)[0] or "application/octet-stream")
    response["Cache-Control"] = "no-cache"
    return response
