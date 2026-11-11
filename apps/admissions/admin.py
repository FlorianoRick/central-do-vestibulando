from django.contrib import admin
from django.utils import timezone

from .models import CalendarEvent, Course, EntranceExam, ExamDocument, ExamPaper, ExamUpdateHistory, Institution, ReviewQueueItem


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "acronym", "institution_type", "state", "is_demo", "is_active")
    list_filter = ("institution_type", "state", "is_demo", "is_active")
    search_fields = ("name", "acronym", "city")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(EntranceExam)
class EntranceExamAdmin(admin.ModelAdmin):
    list_display = ("name", "institution", "process_type", "verification_status", "registration_closes_at", "is_demo", "is_active")
    list_filter = ("verification_status", "process_type", "institution__state", "is_demo", "is_active")
    search_fields = ("name", "institution__name", "institution__acronym")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("courses", "syllabus_subjects")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Identificação", {"fields": ("name", "slug", "institution", "process_type", "description", "is_active", "is_demo")}),
        ("Cursos e programa", {"fields": ("courses", "syllabus_subjects", "syllabus_topics", "exam_format", "admission_criteria", "exam_phases")}),
        ("Vagas e prazos", {"fields": ("positions", "fee_amount", "fee_exemption", "registration_opens_at", "registration_closes_at", "exam_at", "result_at", "enrollment_starts_at", "enrollment_ends_at")}),
        ("Fontes e documentos", {"fields": ("registration_url", "source_url", "candidate_guide_url", "announcement_file", "candidate_guide_file", "notes")}),
        ("Verificação", {"fields": ("verification_status", "verified_at", "verified_by", "created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        changes = {}
        if change:
            previous = EntranceExam.objects.get(pk=obj.pk)
            for field_name in form.changed_data:
                if field_name in {"courses", "syllabus_subjects"}:
                    old_items = getattr(previous, field_name).all()
                    new_items = form.cleaned_data.get(field_name, [])
                    changes[field_name] = {
                        "de": [str(item) for item in old_items],
                        "para": [str(item) for item in new_items],
                    }
                    continue
                old_value = getattr(previous, field_name, "")
                new_value = form.cleaned_data.get(field_name, "")
                changes[field_name] = {"de": str(old_value), "para": str(new_value)}
        if obj.verification_status == EntranceExam.VerificationStatus.CONFIRMED:
            obj.verified_at = obj.verified_at or timezone.now()
            obj.verified_by = request.user
        super().save_model(request, obj, form, change)
        if changes:
            ExamUpdateHistory.objects.create(exam=obj, changed_by=request.user, changes=changes)


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ("title", "exam", "event_type", "starts_at", "verification_status", "is_demo")
    list_filter = ("event_type", "verification_status", "is_demo")
    search_fields = ("title", "exam__name", "exam__institution__name")
    autocomplete_fields = ("exam",)


@admin.register(ExamDocument)
class ExamDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "exam", "document_type", "is_official", "is_demo")
    list_filter = ("document_type", "is_official", "is_demo")
    search_fields = ("title", "exam__name")
    autocomplete_fields = ("exam",)


@admin.register(ExamPaper)
class ExamPaperAdmin(admin.ModelAdmin):
    list_display = ("title", "exam", "year", "paper_type", "subject", "is_official", "is_demo")
    list_filter = ("paper_type", "year", "is_official", "is_demo")
    search_fields = ("title", "exam__name", "exam__institution__name")
    autocomplete_fields = ("exam", "subject")


@admin.register(ExamUpdateHistory)
class ExamUpdateHistoryAdmin(admin.ModelAdmin):
    list_display = ("exam", "changed_at", "changed_by")
    list_filter = ("changed_at",)
    search_fields = ("exam__name", "exam__institution__name")
    readonly_fields = ("exam", "changed_by", "changed_at", "changes")

    def has_add_permission(self, request):
        return False


@admin.register(ReviewQueueItem)
class ReviewQueueItemAdmin(admin.ModelAdmin):
    list_display = ("title", "exam", "status", "discovered_at")
    list_filter = ("status", "discovered_at")
    search_fields = ("title", "exam__name")
    autocomplete_fields = ("exam",)
