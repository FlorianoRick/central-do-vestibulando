from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import CalendarEvent, EntranceExam, Institution


class AdmissionDataTests(TestCase):
    def setUp(self):
        self.institution = Institution.objects.create(
            name="Universidade de Teste",
            acronym="UT",
            slug="universidade-de-teste",
        )

    def test_confirmed_exam_requires_official_source(self):
        exam = EntranceExam(
            name="Vestibular validado",
            slug="vestibular-validado",
            institution=self.institution,
            verification_status=EntranceExam.VerificationStatus.CONFIRMED,
        )
        with self.assertRaises(ValidationError):
            exam.full_clean()

    def test_confirmed_calendar_event_can_be_exported(self):
        exam = EntranceExam.objects.create(
            name="Vestibular confirmado",
            slug="vestibular-confirmado",
            institution=self.institution,
            source_url="https://example.edu.br/edital",
            verification_status=EntranceExam.VerificationStatus.CONFIRMED,
        )
        event = CalendarEvent.objects.create(
            exam=exam,
            title="Prova confirmada",
            starts_at=timezone.now() + timedelta(days=4),
            verification_status=EntranceExam.VerificationStatus.CONFIRMED,
            source_url=exam.source_url,
        )
        response = self.client.get(reverse("admissions:calendar_ics"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, event.title)

    def test_exam_catalog_searches_institution_and_process(self):
        exam = EntranceExam.objects.create(
            name="Processo de Engenharia",
            slug="processo-de-engenharia",
            institution=self.institution,
            is_demo=True,
        )
        response = self.client.get(reverse("admissions:list"), {"q": "Engenharia"})
        self.assertContains(response, exam.name)

    def test_comparison_keeps_selected_order_and_limits_to_three(self):
        exams = [
            EntranceExam.objects.create(name=f"Processo {index}", slug=f"processo-{index}", institution=self.institution, is_demo=True)
            for index in range(4)
        ]
        response = self.client.get(reverse("admissions:compare"), {"id": [str(exam.pk) for exam in exams]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["exams"]), 3)
