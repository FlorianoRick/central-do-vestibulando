from django.contrib import admin

from .models import SiteAppearanceHistory


@admin.register(SiteAppearanceHistory)
class SiteAppearanceHistoryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "changed_by", "appearance")
    list_filter = ("created_at",)
    readonly_fields = ("appearance", "changed_by", "previous_settings", "new_settings", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
