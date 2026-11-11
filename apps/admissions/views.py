import calendar as month_calendar
from datetime import date, datetime, timedelta, timezone as datetime_timezone

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import CalendarEvent, Course, EntranceExam, ExamPaper, Institution


def exam_list(request):
    exams = EntranceExam.objects.filter(is_active=True).select_related("institution").prefetch_related("courses")
    query = request.GET.get("q", "").strip()
    if query:
        exams = exams.filter(
            Q(name__icontains=query)
            | Q(institution__name__icontains=query)
            | Q(institution__acronym__icontains=query)
            | Q(institution__city__icontains=query)
            | Q(institution__state__icontains=query)
            | Q(courses__name__icontains=query)
            | Q(process_type__icontains=query)
        ).distinct()

    state = request.GET.get("state", "").strip().upper()
    region = request.GET.get("region", "").strip()
    process_type = request.GET.get("type", "").strip()
    institution_type = request.GET.get("institution_type", "").strip()
    status = request.GET.get("status", "").strip()
    course = request.GET.get("course", "").strip()
    now = timezone.now()
    if state:
        exams = exams.filter(institution__state=state)
    if region:
        exams = exams.filter(institution__region__iexact=region)
    if process_type:
        exams = exams.filter(process_type=process_type)
    if institution_type:
        exams = exams.filter(institution__institution_type=institution_type)
    if course:
        exams = exams.filter(courses__slug=course)
    if status == "open":
        exams = exams.filter(
            verification_status=EntranceExam.VerificationStatus.CONFIRMED,
            registration_opens_at__lte=now,
            registration_closes_at__gte=now,
            is_demo=False,
        )
    elif status == "closed":
        exams = exams.filter(
            Q(verification_status=EntranceExam.VerificationStatus.CLOSED)
            | Q(verification_status=EntranceExam.VerificationStatus.CONFIRMED, registration_closes_at__lt=now)
        )
    elif status == "upcoming":
        exams = exams.filter(verification_status=EntranceExam.VerificationStatus.CONFIRMED, exam_at__gte=now, is_demo=False)
    elif status == "free":
        exams = exams.filter(fee_amount=0)
    elif status == "exemption":
        exams = exams.exclude(fee_exemption="")

    sort = request.GET.get("sort", "relevance")
    if sort == "deadline":
        exams = exams.order_by(F("registration_closes_at").asc(nulls_last=True), "institution__name")
    elif sort == "date":
        exams = exams.order_by(F("exam_at").asc(nulls_last=True), "institution__name")
    elif sort == "institution":
        exams = exams.order_by("institution__name", "name")
    else:
        exams = exams.order_by("-verification_status", "institution__name", "name")

    page_obj = Paginator(exams, 9).get_page(request.GET.get("page"))
    return render(request, "admissions/exam_list.html", {
        "page_obj": page_obj,
        "exams": page_obj.object_list,
        "query": query,
        "filters": {"state": state, "region": region, "type": process_type, "institution_type": institution_type, "status": status, "course": course, "sort": sort},
        "process_types": EntranceExam.ProcessType.choices,
        "institution_types": Institution.InstitutionType.choices,
        "courses": Course.objects.all(),
        "regions": ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"],
    })


def exam_detail(request, slug):
    exam = get_object_or_404(
        EntranceExam.objects.select_related("institution").prefetch_related("courses", "syllabus_subjects", "documents", "papers"),
        slug=slug,
        is_active=True,
    )
    is_favorite = request.user.is_authenticated and exam.favorited_by.filter(user=request.user).exists()
    return render(request, "admissions/exam_detail.html", {"exam": exam, "is_favorite": is_favorite})


def institution_list(request):
    institutions = Institution.objects.filter(is_active=True).prefetch_related("exams")
    query = request.GET.get("q", "").strip()
    state = request.GET.get("state", "").strip().upper()
    institution_type = request.GET.get("tipo", "").strip()
    if query:
        institutions = institutions.filter(
            Q(name__icontains=query) | Q(acronym__icontains=query) | Q(city__icontains=query) | Q(state__icontains=query)
        ).distinct()
    if state:
        institutions = institutions.filter(state=state)
    if institution_type:
        institutions = institutions.filter(institution_type=institution_type)
    page_obj = Paginator(institutions.order_by("name"), 12).get_page(request.GET.get("page"))
    return render(request, "admissions/institution_list.html", {
        "institutions": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
        "state": state,
        "institution_type": institution_type,
        "institution_types": Institution.InstitutionType.choices,
    })


def exam_compare(request):
    ids = request.GET.getlist("id")
    if len(ids) > 3:
        messages.info(request, "A comparação mostra até três processos seletivos.")
        ids = ids[:3]
    exams = list(EntranceExam.objects.filter(pk__in=ids, is_active=True).select_related("institution").prefetch_related("courses", "syllabus_subjects"))
    exams.sort(key=lambda exam: ids.index(str(exam.pk)) if str(exam.pk) in ids else 0)
    if not exams:
        messages.info(request, "Escolha até três processos na lista para comparar.")
    return render(request, "admissions/compare.html", {"exams": exams})


def calendar(request):
    events = CalendarEvent.objects.filter(exam__is_active=True).select_related("exam", "exam__institution")
    institution = request.GET.get("institution", "").strip()
    selected_exam_ids = [value for value in request.GET.getlist("processo") if value.isdigit()]
    mode = request.GET.get("modo", "lista")
    if institution:
        events = events.filter(exam__institution__slug=institution)
    if selected_exam_ids:
        events = events.filter(exam_id__in=selected_exam_ids)

    reference_date = timezone.localdate()
    month_date = reference_date.replace(day=1)
    week_date = reference_date
    calendar_weeks = []
    if mode == "mes":
        try:
            year, month = map(int, request.GET.get("data", "").split("-"))
            month_date = date(year, month, 1)
        except (ValueError, TypeError):
            month_date = reference_date.replace(day=1)
        if month_date.month == 12:
            end_date = month_date.replace(year=month_date.year + 1, month=1, day=1)
        else:
            end_date = month_date.replace(month=month_date.month + 1, day=1)
        events = events.filter(starts_at__date__gte=month_date, starts_at__date__lt=end_date)
    elif mode == "semana":
        try:
            week_date = date.fromisoformat(request.GET.get("data", ""))
        except ValueError:
            week_date = reference_date
        start_date = week_date - timedelta(days=week_date.weekday())
        end_date = start_date + timedelta(days=7)
        events = events.filter(starts_at__date__gte=start_date, starts_at__date__lt=end_date)
    else:
        mode = "lista"
        events = events.filter(starts_at__date__gte=reference_date)

    events = list(events.order_by("starts_at"))
    exam_dates = {}
    for event in events:
        if event.event_type == CalendarEvent.EventType.EXAM:
            exam_dates.setdefault(event.starts_at.date(), set()).add(event.exam_id)
    for event in events:
        event.is_conflict = event.event_type == CalendarEvent.EventType.EXAM and len(exam_dates.get(event.starts_at.date(), set())) > 1
    events_by_day = {}
    for event in events:
        events_by_day.setdefault(event.starts_at.date(), []).append(event)
    if mode == "mes":
        for week in month_calendar.Calendar(firstweekday=0).monthdatescalendar(month_date.year, month_date.month):
            calendar_weeks.append([
                {"date": day, "is_current_month": day.month == month_date.month, "events": events_by_day.get(day, [])}
                for day in week
            ])
    elif mode == "semana":
        week_start = week_date - timedelta(days=week_date.weekday())
        calendar_days = [
            {"date": week_start + timedelta(days=index), "events": events_by_day.get(week_start + timedelta(days=index), [])}
            for index in range(7)
        ]
    else:
        calendar_days = []
    favorite_event_ids = set()
    if request.user.is_authenticated:
        from apps.accounts.models import FavoriteCalendarEvent

        favorite_event_ids = set(FavoriteCalendarEvent.objects.filter(user=request.user).values_list("event_id", flat=True))
    return render(request, "admissions/calendar.html", {
        "events": events,
        "mode": mode,
        "calendar_weeks": calendar_weeks,
        "calendar_days": calendar_days if mode == "semana" else [],
        "today": reference_date,
        "month_value": month_date.strftime("%Y-%m"),
        "week_value": week_date.isoformat(),
        "weekdays": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
        "institutions": Institution.objects.filter(is_active=True).order_by("name"),
        "exams": EntranceExam.objects.filter(is_active=True).select_related("institution").order_by("institution__name", "name"),
        "selected_institution": institution,
        "selected_exam_ids": selected_exam_ids,
        "favorite_event_ids": favorite_event_ids,
    })


def calendar_ics(request):
    events = CalendarEvent.objects.filter(
        starts_at__gte=timezone.now(),
        verification_status=EntranceExam.VerificationStatus.CONFIRMED,
        is_demo=False,
        exam__is_demo=False,
        exam__is_active=True,
    ).select_related("exam", "exam__institution").order_by("starts_at")

    def escape(value):
        return str(value).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Central do Vestibulando//Calendario//PT-BR", "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    for event in events:
        start = event.starts_at.astimezone(datetime_timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        end_value = event.ends_at or (event.starts_at + timedelta(hours=1))
        end = end_value.astimezone(datetime_timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:cv-{event.pk}@centraldovestibulando.local",
            f"DTSTAMP:{timezone.now().astimezone(datetime_timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{start}",
            f"DTEND:{end}",
            f"SUMMARY:{escape(event.title)} — {escape(event.exam.institution.acronym or event.exam.institution.name)}",
            f"DESCRIPTION:{escape(event.exam.name)}",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    response = HttpResponse("\r\n".join(lines), content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="calendario-vestibulares.ics"'
    return response


def paper_list(request, area=None):
    papers = ExamPaper.objects.filter(exam__is_active=True).select_related("exam", "exam__institution", "subject")
    query = request.GET.get("q", "").strip()
    year = request.GET.get("ano", "").strip()
    subject = request.GET.get("materia", "").strip()
    paper_type = request.GET.get("tipo", "").strip()
    area = (area or request.GET.get("area", "provas")).strip()
    if query:
        papers = papers.filter(Q(title__icontains=query) | Q(exam__name__icontains=query) | Q(exam__institution__name__icontains=query) | Q(exam__institution__acronym__icontains=query))
    if year.isdigit():
        papers = papers.filter(year=int(year))
    if subject:
        papers = papers.filter(subject__slug=subject)
    if paper_type:
        papers = papers.filter(paper_type=paper_type)
    if area == "gabaritos":
        papers = papers.exclude(Q(answer_key_file="") & Q(answer_key_url=""))
    page_obj = Paginator(papers, 12).get_page(request.GET.get("page"))
    from apps.studies.models import StudySubject
    return render(request, "admissions/paper_list.html", {
        "papers": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
        "year": year,
        "selected_subject": subject,
        "paper_type": paper_type,
        "area": area,
        "subjects": StudySubject.objects.all(),
        "paper_types": ExamPaper.PaperType.choices,
    })
