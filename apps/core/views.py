from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from apps.admissions.models import CalendarEvent, EntranceExam
from apps.appearance.services import get_active_appearance
from apps.news.models import NewsArticle
from apps.studies.models import StudyResource


HOME_SECTION_TEMPLATES = {
    "exam_overview": "core/partials/home_exam_overview.html",
    "updates": "core/partials/home_updates.html",
    "featured_exams": "core/partials/home_featured_exams.html",
    "materials": "core/partials/home_materials.html",
}


def home(request):
    appearance = get_active_appearance(request)
    now = timezone.now()
    confirmed = EntranceExam.objects.filter(
        is_active=True,
        verification_status=EntranceExam.VerificationStatus.CONFIRMED,
        is_demo=False,
    ).select_related("institution")
    open_exams = EntranceExam.objects.none()
    if appearance.show_home_open_exams:
        open_exams = confirmed.filter(
            registration_opens_at__lte=now,
            registration_closes_at__gte=now,
        )[:4]

    upcoming_exams = EntranceExam.objects.none()
    if appearance.show_home_upcoming_exams:
        upcoming_exams = confirmed.filter(exam_at__gte=now).order_by("exam_at")[:4]

    upcoming_results = EntranceExam.objects.none()
    if appearance.show_home_results:
        upcoming_results = confirmed.filter(result_at__gte=now).order_by("result_at")[:4]

    upcoming_events = CalendarEvent.objects.none()
    if appearance.show_home_event_panel:
        upcoming_events = CalendarEvent.objects.filter(
            starts_at__gte=now,
            verification_status=EntranceExam.VerificationStatus.CONFIRMED,
            is_demo=False,
            exam__is_active=True,
        ).select_related("exam", "exam__institution")[:5]

    examples = EntranceExam.objects.none()
    if appearance.show_home_featured_exams:
        examples = EntranceExam.objects.filter(
            is_active=True,
            institution__is_active=True,
            is_demo=True,
        ).select_related("institution")[:appearance.featured_exam_count]

    recent_news = NewsArticle.objects.none()
    if appearance.show_home_news:
        recent_news = NewsArticle.objects.filter(
            is_published=True,
        ).filter(
            Q(is_demo=True)
            | Q(
                is_demo=False,
                review_status=NewsArticle.ReviewStatus.VERIFIED,
                source_checked_at__isnull=False,
                published_at__isnull=False,
                published_at__lte=now,
                source_url__gt="",
            )
        ).filter(
            Q(published_at__isnull=True) | Q(published_at__lte=now)
        ).select_related("institution")[:3]
    home_materials = StudyResource.objects.none()
    if appearance.show_home_materials:
        home_materials = StudyResource.objects.filter(
            is_published=True,
            subject__is_active=True,
            source_name__gt="",
            source_url__gt="",
            last_checked_at__isnull=False,
        ).select_related("subject")[:2]
    section_visibility = {
        "exam_overview": (
            appearance.show_home_event_panel
            and (appearance.show_home_upcoming_exams or appearance.show_home_open_exams)
        ),
        "updates": appearance.show_home_results or appearance.show_home_news,
        "featured_exams": appearance.show_home_featured_exams,
        "materials": appearance.show_home_news or appearance.show_home_materials,
    }
    section_order = [
        "materials" if key == "institutions" else key
        for key in appearance.home_section_order
    ]
    home_sections = [
        {"key": key, "template": HOME_SECTION_TEMPLATES[key]}
        for key in section_order
        if key in HOME_SECTION_TEMPLATES and section_visibility.get(key, False)
    ]
    return render(request, "core/home.html", {
        "open_exams": open_exams,
        "upcoming_exams": upcoming_exams,
        "upcoming_results": upcoming_results,
        "upcoming_events": upcoming_events,
        "recent_news": recent_news,
        "examples": examples,
        "home_materials": home_materials,
        "home_sections": home_sections,
    })


def privacy(request):
    return render(request, "core/privacy.html")


def terms(request):
    return render(request, "core/terms.html")
