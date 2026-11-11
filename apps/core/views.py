from django.shortcuts import render
from django.utils import timezone

from apps.admissions.models import CalendarEvent, EntranceExam, Institution
from apps.news.models import NewsArticle


def home(request):
    now = timezone.now()
    confirmed = EntranceExam.objects.filter(
        is_active=True,
        verification_status=EntranceExam.VerificationStatus.CONFIRMED,
        is_demo=False,
    ).select_related("institution")
    open_exams = confirmed.filter(registration_opens_at__lte=now, registration_closes_at__gte=now)[:4]
    upcoming_exams = confirmed.filter(exam_at__gte=now).order_by("exam_at")[:4]
    upcoming_results = confirmed.filter(result_at__gte=now).order_by("result_at")[:4]
    upcoming_events = CalendarEvent.objects.filter(
        starts_at__gte=now,
        verification_status=EntranceExam.VerificationStatus.CONFIRMED,
        is_demo=False,
        exam__is_active=True,
    ).select_related("exam", "exam__institution")[:5]
    examples = EntranceExam.objects.filter(is_active=True, is_demo=True).select_related("institution")[:4]
    institutions = Institution.objects.filter(is_active=True).order_by("name")[:6]
    recent_news = NewsArticle.objects.filter(is_published=True, is_demo=False, published_at__isnull=False).select_related("institution")[:3]
    return render(request, "core/home.html", {
        "open_exams": open_exams,
        "upcoming_exams": upcoming_exams,
        "upcoming_results": upcoming_results,
        "upcoming_events": upcoming_events,
        "recent_news": recent_news,
        "examples": examples,
        "institutions": institutions,
    })


def privacy(request):
    return render(request, "core/privacy.html")


def terms(request):
    return render(request, "core/terms.html")
