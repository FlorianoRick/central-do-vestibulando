from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.admissions.models import EntranceExam, Institution
from .models import StudyPlan, StudySession, StudySubject

User = get_user_model()


class StudyPlannerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="estudante", password="Preparacao-segura-741!")
        self.subject = StudySubject.objects.create(name="História", slug="historia")
        self.institution = Institution.objects.create(name="Universidade demonstrativa", slug="universidade-demo", is_demo=True)
        self.exam = EntranceExam.objects.create(name="Processo demonstrativo", slug="processo-demo", institution=self.institution, is_demo=True)

    def test_plan_creation_generates_editable_week(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("studies:planner"), {
            "title": "Plano de revisão",
            "target_exams": [str(self.exam.pk)],
            "subjects": [str(self.subject.pk)],
            "weekly_hours": "6",
            "daily_goal_minutes": "45",
            "notes": "Priorizar revisões.",
        })
        plan = StudyPlan.objects.get(user=self.user)
        self.assertRedirects(response, reverse("studies:plan_detail", args=[plan.pk]))
        self.assertEqual(plan.sessions.count(), 7)
        self.assertContains(self.client.get(reverse("studies:plan_detail", args=[plan.pk])), "Sessões planejadas")

    def test_student_cannot_open_another_users_plan(self):
        other = User.objects.create_user(username="outra", password="Preparacao-segura-741!")
        plan = StudyPlan.objects.create(user=other, title="Privado")
        self.client.force_login(self.user)
        response = self.client.get(reverse("studies:plan_detail", args=[plan.pk]))
        self.assertEqual(response.status_code, 404)

    def test_session_update_is_limited_to_plan_owner(self):
        other = User.objects.create_user(username="outra", password="Preparacao-segura-741!")
        plan = StudyPlan.objects.create(user=other, title="Privado")
        plan.subjects.add(self.subject)
        session = StudySession.objects.create(plan=plan, subject=self.subject, scheduled_for="2026-11-12", duration_minutes=45)
        self.client.force_login(self.user)
        response = self.client.post(reverse("studies:update_session", args=[plan.pk, session.pk]), {"action": "toggle"})
        self.assertEqual(response.status_code, 404)
        session.refresh_from_db()
        self.assertEqual(session.status, StudySession.SessionStatus.PLANNED)

    def test_student_can_edit_and_archive_own_plan(self):
        plan = StudyPlan.objects.create(user=self.user, title="Plano inicial")
        self.client.force_login(self.user)
        response = self.client.post(reverse("studies:edit_plan", args=[plan.pk]), {
            "title": "Plano atualizado",
            "target_exams": [str(self.exam.pk)],
            "subjects": [str(self.subject.pk)],
            "weekly_hours": "8",
            "daily_goal_minutes": "50",
            "notes": "",
        })
        self.assertRedirects(response, reverse("studies:plan_detail", args=[plan.pk]))
        plan.refresh_from_db()
        self.assertEqual(plan.title, "Plano atualizado")
        response = self.client.post(reverse("studies:archive_plan", args=[plan.pk]))
        self.assertRedirects(response, reverse("studies:planner"))
        plan.refresh_from_db()
        self.assertFalse(plan.is_active)
