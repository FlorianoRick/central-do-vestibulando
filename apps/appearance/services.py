from decimal import Decimal

from django.db import models

from .models import SiteAppearance, SiteAppearanceHistory


EXCLUDED_SNAPSHOT_FIELDS = {
    "singleton_key",
    "updated_at",
    "last_modified_by",
    "draft_settings",
    "draft_saved_at",
    "draft_saved_by",
}


def get_active_appearance(request=None):
    if request is not None and hasattr(request, "site_appearance"):
        return request.site_appearance
    appearance, _created = SiteAppearance.objects.get_or_create(pk=1)
    if request is not None:
        request.site_appearance = appearance
    return appearance


def configuration_snapshot(appearance):
    snapshot = {}
    for field in appearance._meta.fields:
        if field.name in EXCLUDED_SNAPSHOT_FIELDS:
            continue
        value = getattr(appearance, field.name)
        if isinstance(field, models.FileField):
            value = value.name or ""
        elif isinstance(value, Decimal):
            value = str(value)
        snapshot[field.name] = value
    return snapshot


def restore_default_values(appearance):
    for field in appearance._meta.fields:
        if field.name in EXCLUDED_SNAPSHOT_FIELDS:
            continue
        setattr(appearance, field.name, field.get_default())
    return appearance


def record_configuration_change(appearance, changed_by, previous, current):
    if previous == current:
        return None
    return SiteAppearanceHistory.objects.create(
        appearance=appearance,
        changed_by=changed_by,
        previous_settings=previous,
        new_settings=current,
    )


def remove_replaced_assets(old_asset_names, appearance):
    for field_name, old_name in old_asset_names.items():
        new_name = getattr(appearance, field_name).name or ""
        if old_name and old_name != new_name:
            getattr(appearance, field_name).storage.delete(old_name)
