from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.admissions.models import EntranceExam, Institution
from apps.appearance.services import get_active_appearance
from apps.news.models import NewsArticle
from apps.studies.models import StudyMaterial, StudyResource, StudySubject


class DemoCatalogTests(TestCase):
    def test_seed_keeps_only_the_curated_active_institution_catalog(self):
        call_command("seed_demo_data", stdout=StringIO())

        expected_slugs = {"fatec", "unesp", "unicamp", "usp", "puc-sp"}
        institutions = Institution.objects.filter(is_active=True)
        self.assertSetEqual(set(institutions.values_list("slug", flat=True)), expected_slugs)
        self.assertFalse(institutions.filter(is_demo=True).exists())
        self.assertSetEqual(
            set(
                EntranceExam.objects.filter(
                    is_active=True,
                    institution__is_active=True,
                ).values_list("institution__slug", flat=True)
            ),
            expected_slugs,
        )
        self.assertEqual(
            set(StudySubject.objects.filter(is_active=True).values_list("name", flat=True)),
            {
                "Biologia", "Filosofia", "Física", "Geografia", "História",
                "Inglês", "Literatura", "Matemática", "Química", "Sociologia",
                "Língua Portuguesa",
            },
        )


class StarterContentTests(TestCase):
    def setUp(self):
        call_command("seed_demo_data", stdout=StringIO())
        call_command("seed_vestibulando_content", stdout=StringIO())

    def test_seed_adds_verified_resources_for_all_active_subjects_and_three_news_items(self):
        self.assertEqual(
            StudyResource.objects.filter(
                is_published=True,
                subject__is_active=True,
                source_url__gt="",
                last_checked_at__isnull=False,
            ).count(),
            11,
        )
        self.assertEqual(
            NewsArticle.objects.filter(
                is_published=True,
                is_demo=False,
                review_status=NewsArticle.ReviewStatus.VERIFIED,
                source_checked_at__isnull=False,
            ).count(),
            3,
        )

    def test_seed_is_idempotent(self):
        call_command("seed_vestibulando_content", stdout=StringIO())
        self.assertEqual(StudyResource.objects.count(), 11)
        self.assertEqual(
            NewsArticle.objects.filter(is_demo=False).count(),
            3,
        )

    def test_resource_and_verified_news_appear_in_public_pages(self):
        home = self.client.get(reverse("core:home"))
        materials = self.client.get(reverse("studies:list"))
        news = self.client.get(reverse("news:list"))
        self.assertContains(home, "Materiais e guias")
        self.assertContains(materials, "Simple Present")
        self.assertContains(news, "Unicamp divulga convocados para a segunda fase")

    def test_legacy_home_section_order_still_renders_materials(self):
        appearance = get_active_appearance()
        appearance.home_section_order = [
            "exam_overview",
            "updates",
            "featured_exams",
            "institutions",
        ]
        appearance.save(update_fields=["home_section_order"])

        home = self.client.get(reverse("core:home"))

        self.assertContains(home, "Materiais e guias")


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
            reverse("admissions:detail", args=[self.exam.slug]),
            reverse("admissions:compare"),
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

    def test_calendar_and_institution_pages_are_not_public_routes(self):
        self.assertEqual(self.client.get("/vestibulares/calendario/").status_code, 404)
        self.assertEqual(self.client.get("/vestibulares/instituicoes/").status_code, 404)

    def test_private_planner_redirects_to_login(self):
        response = self.client.get(reverse("studies:planner"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('studies:planner')}")

    def test_account_and_planner_render_for_student(self):
        user = get_user_model().objects.create_user(username="estudante", password="Preparacao-segura-741!")
        self.client.force_login(user)
        self.assertContains(self.client.get(reverse("accounts:account")), "Meus dados")
        self.assertContains(self.client.get(reverse("studies:planner")), "Novo plano")

    def test_unverified_exam_never_displays_official_registration_claim(self):
        response = self.client.get(reverse("admissions:detail", args=[self.exam.slug]))
        self.assertContains(response, "Verificação necessária")
        self.assertContains(response, "Não há datas ou links oficiais confirmados", status_code=200)

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
