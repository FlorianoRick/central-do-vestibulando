from datetime import datetime, timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.admissions.models import CalendarEvent, EntranceExam, Institution
from apps.news.models import NewsArticle
from apps.studies.models import StudyMaterial, StudySubject


class DemoCatalogTests(TestCase):
    def test_original_demo_institutions_and_processes_are_available(self):
        call_command("seed_demo_data", stdout=StringIO())

        expected_slugs = {
            "inep", "usp", "unicamp", "unesp", "fatec", "unifesp", "ufrgs",
            "ufpr", "uerj", "unb", "ifsp", "sisu", "prouni", "fies",
        }
        institutions = Institution.objects.filter(slug__in=expected_slugs)
        self.assertSetEqual(set(institutions.values_list("slug", flat=True)), expected_slugs)
        self.assertEqual(institutions.filter(is_demo=True).count(), len(expected_slugs))
        self.assertEqual(EntranceExam.objects.filter(is_demo=True).count(), len(expected_slugs))


class PublicPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.institution = Institution.objects.create(
            name="Universidade de Exemplo",
            acronym="UEX",
            slug="uex",
            institution_type=Institution.InstitutionType.STATE,
            is_demo=True,
        )
        cls.exam = EntranceExam.objects.create(
            name="Vestibular demonstrativo",
            slug="vestibular-demonstrativo",
            institution=cls.institution,
            is_demo=True,
        )
        cls.subject = StudySubject.objects.create(name="Matemática", slug="matematica")
        cls.material = StudyMaterial.objects.create(
            subject=cls.subject,
            title="Guia demonstrativo",
            slug="guia-demonstrativo",
            summary="Um guia de exemplo.",
            content="Conteúdo de demonstração.",
            is_demo=True,
        )
        cls.article = NewsArticle.objects.create(
            title="Guia demonstrativo de edital",
            slug="guia-demonstrativo-edital",
            summary="Como encontrar informações em um edital.",
            content="Texto de exemplo.",
            is_demo=True,
        )

    def test_public_pages_render(self):
        urls = [
            reverse("core:home"),
            reverse("core:privacy"),
            reverse("core:terms"),
            reverse("admissions:list"),
            reverse("admissions:institutions"),
            reverse("admissions:detail", args=[self.exam.slug]),
            reverse("admissions:compare"),
            reverse("admissions:calendar"),
            reverse("admissions:calendar") + "?modo=mes&data=2026-11",
            reverse("admissions:calendar") + "?modo=semana&data=2026-11-11",
            reverse("admissions:papers"),
            reverse("admissions:answer_keys"),
            reverse("studies:list"),
            reverse("studies:detail", args=[self.material.slug]),
            reverse("studies:compare"),
            reverse("news:list"),
            reverse("news:detail", args=[self.article.slug]),
            reverse("accounts:login"),
            reverse("accounts:register"),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_private_planner_redirects_to_login(self):
        response = self.client.get(reverse("studies:planner"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('studies:planner')}")

    def test_calendar_month_and_week_visualizations_render(self):
        from django.utils import timezone

        event = CalendarEvent.objects.create(
            exam=self.exam,
            title="Prova demonstrativa",
            event_type=CalendarEvent.EventType.EXAM,
            starts_at=timezone.make_aware(datetime(2030, 11, 12, 9, 0)),
            is_demo=True,
        )
        month_response = self.client.get(reverse("admissions:calendar"), {"modo": "mes", "data": "2030-11"})
        week_response = self.client.get(reverse("admissions:calendar"), {"modo": "semana", "data": "2030-11-12"})
        self.assertContains(month_response, event.title)
        self.assertContains(week_response, event.title)

    def test_account_and_planner_render_for_student(self):
        user = get_user_model().objects.create_user(username="estudante", password="Preparacao-segura-741!")
        self.client.force_login(user)
        self.assertContains(self.client.get(reverse("accounts:account")), "Meus dados")
        self.assertContains(self.client.get(reverse("studies:planner")), "Novo plano")

    def test_unverified_exam_never_displays_official_registration_claim(self):
        response = self.client.get(reverse("admissions:detail", args=[self.exam.slug]))
        self.assertContains(response, "Verificação necessária")
        self.assertContains(response, "Não há datas ou links oficiais confirmados", status_code=200)

    def test_calendar_export_excludes_unverified_events(self):
        from django.utils import timezone
        from datetime import timedelta

        CalendarEvent.objects.create(
            exam=self.exam,
            title="Prazo demonstrativo",
            starts_at=timezone.now() + timedelta(days=2),
            is_demo=True,
        )
        response = self.client.get(reverse("admissions:calendar_ics"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Prazo demonstrativo")
        self.assertContains(response, "BEGIN:VCALENDAR")

    def test_syllabus_comparison_lists_shared_subjects(self):
        second_exam = EntranceExam.objects.create(
            name="Outro vestibular demonstrativo",
            slug="outro-vestibular-demonstrativo",
            institution=self.institution,
            is_demo=True,
        )
        self.exam.syllabus_subjects.add(self.subject)
        second_exam.syllabus_subjects.add(self.subject)
        response = self.client.get(reverse("studies:compare"), {"exams": [self.exam.pk, second_exam.pk]})
        self.assertContains(response, "Matemática")
