from django.contrib import admin

from .models import MockExamResult, StudyMaterial, StudyPlan, StudyResource, StudySession, StudySubject


@admin.register(StudySubject)
class StudySubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(StudyResource)
class StudyResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "source_name", "last_checked_at", "is_published")
    list_filter = ("subject", "is_published", "source_name")
    search_fields = ("title", "description", "source_name")
    autocomplete_fields = ("subject",)


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "material_type", "is_official", "is_demo", "is_published")
    list_filter = ("subject", "material_type", "is_official", "is_demo", "is_published")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("subject",)


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "weekly_hours", "is_active", "updated_at")
    list_filter = ("is_active", "updated_at")
    search_fields = ("title", "user__username", "user__email")
    filter_horizontal = ("subjects", "target_exams")


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ("subject", "plan", "scheduled_for", "duration_minutes", "status")
    list_filter = ("status", "scheduled_for", "subject")
    search_fields = ("topic", "subject__name", "plan__user__username")
    autocomplete_fields = ("plan", "subject")


@admin.register(MockExamResult)
class MockExamResultAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "exam", "taken_on", "score", "maximum_score")
    list_filter = ("taken_on",)
    search_fields = ("title", "user__username", "exam__name")
