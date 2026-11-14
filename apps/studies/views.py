from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import MockExamResultForm, StudyPlanForm, StudySessionForm, SyllabusCompareForm
from .models import MockExamResult, StudyMaterial, StudyPlan, StudyResource, StudySession, StudySubject


def material_list(request):
    subjects = StudySubject.objects.filter(is_active=True)
    selected_subject = request.GET.get("materia", "").strip()
    materials = StudyMaterial.objects.filter(
        is_published=True,
        subject__is_active=True,
    ).select_related("subject")
    resources = StudyResource.objects.filter(
        is_published=True,
        subject__is_active=True,
        source_name__gt="",
        source_url__gt="",
        last_checked_at__isnull=False,
    ).select_related("subject")
    if selected_subject:
        materials = materials.filter(subject__slug=selected_subject)
        resources = resources.filter(subject__slug=selected_subject)
    query = request.GET.get("q", "").strip()
    if query:
        materials = materials.filter(Q(title__icontains=query) | Q(summary__icontains=query) | Q(content__icontains=query))
        resources = resources.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(source_name__icontains=query)
        )
    page_obj = Paginator(materials, 10).get_page(request.GET.get("page"))
    return render(request, "studies/material_list.html", {
        "subjects": subjects,
        "selected_subject": selected_subject,
        "resources": resources,
        "materials": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
        "result_count": page_obj.paginator.count + resources.count(),
    })


def material_detail(request, slug):
    material = get_object_or_404(
        StudyMaterial.objects.select_related("subject"),
        slug=slug,
        is_published=True,
        subject__is_active=True,
    )
    is_saved = request.user.is_authenticated and material.saved_by.filter(user=request.user).exists()
    return render(request, "studies/material_detail.html", {"material": material, "is_saved": is_saved})


def syllabus_compare(request):
    form = SyllabusCompareForm(request.GET or None)
    exams = []
    shared_subjects = []
    unique_subjects = {}
    shared_topics = []
    unique_topics = {}
    if request.GET and form.is_valid():
        exams = list(form.cleaned_data["exams"])
        subject_sets = [set(exam.syllabus_subjects.all()) for exam in exams]
        if subject_sets:
            shared_subjects = sorted(set.intersection(*subject_sets), key=lambda subject: subject.name)
            for exam, subject_set in zip(exams, subject_sets):
                unique_subjects[exam.pk] = sorted(subject_set.difference(shared_subjects), key=lambda subject: subject.name)
        topic_lines = {
            exam.pk: [line.strip() for line in exam.syllabus_topics.splitlines() if line.strip()]
            for exam in exams
        }
        normalized_topics = {
            exam_id: {topic.casefold(): topic for topic in topics}
            for exam_id, topics in topic_lines.items()
        }
        if normalized_topics:
            shared_topic_keys = set.intersection(*(set(topics) for topics in normalized_topics.values()))
            first_exam_topics = next(iter(normalized_topics.values()))
            shared_topics = [first_exam_topics[key] for key in sorted(shared_topic_keys)]
            for exam in exams:
                unique_topics[exam.pk] = [
                    topic for key, topic in normalized_topics[exam.pk].items() if key not in shared_topic_keys
                ]
    return render(request, "studies/syllabus_compare.html", {
        "form": form,
        "exams": exams,
        "shared_subjects": shared_subjects,
        "unique_subjects": unique_subjects,
        "shared_topics": shared_topics,
        "unique_topics": unique_topics,
    })


@login_required
def planner(request):
    form = StudyPlanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        plan = form.save(commit=False)
        plan.user = request.user
        plan.save()
        form.save_m2m()
        selected_subjects = list(plan.subjects.all())
        if selected_subjects:
            subject_overlap = {subject.pk: 0 for subject in selected_subjects}
            verified_exams = [
                exam
                for exam in plan.target_exams.prefetch_related("syllabus_subjects")
                if exam.officially_verified
            ]
            for exam in verified_exams:
                for subject in exam.syllabus_subjects.all():
                    if subject.pk in subject_overlap:
                        subject_overlap[subject.pk] += 1
            selected_subjects.sort(key=lambda subject: (-subject_overlap[subject.pk], subject.name.casefold()))
            minutes = max(10, min(plan.daily_goal_minutes, plan.weekly_hours * 60 // 7))
            start = timezone.localdate() + timedelta(days=1)
            for day in range(7):
                subject = selected_subjects[day % len(selected_subjects)]
                StudySession.objects.create(
                    plan=plan,
                    subject=subject,
                    scheduled_for=start + timedelta(days=day),
                    duration_minutes=minutes,
                    topic="Revisão de conteúdo",
                )
        messages.success(request, "Plano criado com uma sugestão de sessões para a próxima semana.")
        return redirect("studies:plan_detail", plan_id=plan.pk)

    plans = StudyPlan.objects.filter(user=request.user, is_active=True).prefetch_related("subjects", "target_exams")
    results = MockExamResult.objects.filter(user=request.user).select_related("exam", "exam__institution")[:8]
    return render(request, "studies/planner.html", {"form": form, "plans": plans, "results": results, "result_form": MockExamResultForm()})


@login_required
def plan_detail(request, plan_id):
    plan = get_object_or_404(StudyPlan.objects.prefetch_related("subjects", "target_exams"), pk=plan_id, user=request.user)
    sessions = plan.sessions.select_related("subject")
    completed = sessions.filter(status=StudySession.SessionStatus.COMPLETED)
    session_form = StudySessionForm()
    session_form.fields["subject"].queryset = plan.subjects.all()
    context = {
        "plan": plan,
        "sessions": sessions,
        "completed_count": completed.count(),
        "total_hours": sum(session.duration_minutes for session in completed) / 60,
        "session_form": session_form,
    }
    return render(request, "studies/plan_detail.html", context)


@login_required
def edit_plan(request, plan_id):
    plan = get_object_or_404(StudyPlan, pk=plan_id, user=request.user)
    form = StudyPlanForm(request.POST or None, instance=plan)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Seu plano foi atualizado.")
        return redirect("studies:plan_detail", plan_id=plan.pk)
    return render(request, "studies/plan_edit.html", {"plan": plan, "form": form})


@login_required
@require_POST
def archive_plan(request, plan_id):
    plan = get_object_or_404(StudyPlan, pk=plan_id, user=request.user)
    plan.is_active = False
    plan.save(update_fields=["is_active", "updated_at"])
    messages.info(request, "Plano arquivado. Suas sessões e resultados foram preservados.")
    return redirect("studies:planner")


@login_required
@require_POST
def add_session(request, plan_id):
    plan = get_object_or_404(StudyPlan, pk=plan_id, user=request.user)
    form = StudySessionForm(request.POST)
    form.fields["subject"].queryset = plan.subjects.all()
    if form.is_valid():
        session = form.save(commit=False)
        session.plan = plan
        if session.status == StudySession.SessionStatus.COMPLETED:
            session.completed_at = timezone.now()
        session.save()
        messages.success(request, "Sessão adicionada ao seu plano.")
    else:
        messages.error(request, "Revise os dados da sessão e tente novamente.")
    return redirect("studies:plan_detail", plan_id=plan.pk)


@login_required
@require_POST
def update_session(request, plan_id, session_id):
    plan = get_object_or_404(StudyPlan, pk=plan_id, user=request.user)
    session = get_object_or_404(StudySession, pk=session_id, plan=plan)
    if request.POST.get("action") == "delete":
        session.delete()
        messages.info(request, "Sessão removida do plano.")
        return redirect("studies:plan_detail", plan_id=plan.pk)
    if request.POST.get("action") == "toggle":
        session.status = StudySession.SessionStatus.PLANNED if session.status == StudySession.SessionStatus.COMPLETED else StudySession.SessionStatus.COMPLETED
        session.completed_at = timezone.now() if session.status == StudySession.SessionStatus.COMPLETED else None
        session.save(update_fields=["status", "completed_at"])
        messages.success(request, "Progresso da sessão atualizado.")
        return redirect("studies:plan_detail", plan_id=plan.pk)
    form = StudySessionForm(request.POST, instance=session)
    form.fields["subject"].queryset = plan.subjects.all()
    if form.is_valid():
        session = form.save(commit=False)
        session.completed_at = timezone.now() if session.status == StudySession.SessionStatus.COMPLETED else None
        session.save()
        messages.success(request, "Sessão atualizada.")
    else:
        messages.error(request, "Revise os dados da sessão.")
    return redirect("studies:plan_detail", plan_id=plan.pk)


@login_required
@require_POST
def add_mock_result(request):
    form = MockExamResultForm(request.POST)
    if form.is_valid():
        result = form.save(commit=False)
        result.user = request.user
        result.save()
        messages.success(request, "Resultado do simulado registrado.")
    else:
        messages.error(request, "Revise os dados do simulado.")
    return redirect("studies:planner")
