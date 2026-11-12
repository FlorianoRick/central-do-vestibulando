from django.shortcuts import render
from django.utils import timezone

from apps.admissions.models import CalendarEvent, EntranceExam, Institution
from apps.appearance.services import get_active_appearance
from apps.news.models import NewsArticle


HOME_SECTION_TEMPLATES = {
    "exam_overview": "core/partials/home_exam_overview.html",
    "updates": "core/partials/home_updates.html",
    "featured_exams": "core/partials/home_featured_exams.html",
    "institutions": "core/partials/home_institutions.html",
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
        examples = EntranceExam.objects.filter(is_active=True, is_demo=True).select_related("institution")[:appearance.featured_exam_count]

    institutions = Institution.objects.none()
    if appearance.show_home_institutions:
        institutions = Institution.objects.filter(is_active=True).order_by("name")[:6]

    recent_news = NewsArticle.objects.none()
    if appearance.show_home_news:
        recent_news = NewsArticle.objects.filter(
            is_published=True,
            is_demo=False,
            published_at__isnull=False,
        ).select_related("institution")[:3]
    home_sections = [
        {"key": key, "template": HOME_SECTION_TEMPLATES[key]}
        for key in appearance.home_section_order
        if key in HOME_SECTION_TEMPLATES
    ]
    return render(request, "core/home.html", {
        "open_exams": open_exams,
        "upcoming_exams": upcoming_exams,
        "upcoming_results": upcoming_results,
        "upcoming_events": upcoming_events,
        "recent_news": recent_news,
        "examples": examples,
        "institutions": institutions,
        "home_sections": home_sections,
    })


def privacy(request):
    return render(request, "core/privacy.html")


def terms(request):
    return render(request, "core/terms.html")
