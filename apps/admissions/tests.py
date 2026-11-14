from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import EntranceExam, ExamArchiveDocument, Institution


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

    def test_published_archive_document_requires_a_real_pdf_and_verified_source(self):
        exam = EntranceExam.objects.create(
            name="Vestibular confirmado",
            slug="vestibular-confirmado",
            institution=self.institution,
            source_url="https://example.edu.br/edital",
            verification_status=EntranceExam.VerificationStatus.CONFIRMED,
        )
        document = ExamArchiveDocument(
            exam=exam,
            title="Prova anterior",
            document_type=ExamArchiveDocument.DocumentType.EXAM,
            publication_status=ExamArchiveDocument.PublicationStatus.PUBLISHED,
            source_url="https://example.edu.br/acervo",
            source_checked_at=timezone.localdate(),
            file=SimpleUploadedFile(
                "prova.pdf",
                b"%PDF-1.4\nconteudo de teste",
                content_type="application/pdf",
            ),
        )
        document.full_clean()
        document.file = SimpleUploadedFile(
            "prova.pdf",
            b"isto nao e um pdf",
            content_type="application/pdf",
        )
        with self.assertRaises(ValidationError) as error:
            document.full_clean()
        self.assertIn("file", error.exception.message_dict)

    def test_archive_download_hides_unpublished_records_from_public(self):
        exam = EntranceExam.objects.create(
            name="Processo em rascunho",
            slug="processo-em-rascunho",
            institution=self.institution,
            is_demo=True,
        )
        document = ExamArchiveDocument.objects.create(
            exam=exam,
            title="Documento não publicado",
            document_type=ExamArchiveDocument.DocumentType.EXAM,
            publication_status=ExamArchiveDocument.PublicationStatus.DRAFT,
        )
        response = self.client.get(reverse("admissions:archive_download", args=[document.pk]))
        self.assertEqual(response.status_code, 404)

    def test_exam_catalog_searches_institution_and_process(self):
        exam = EntranceExam.objects.create(
            name="Processo de Engenharia",
            slug="processo-de-engenharia",
            institution=self.institution,
            is_demo=True,
        )
        response = self.client.get(reverse("admissions:list"), {"q": "Engenharia"})
        self.assertContains(response, exam.name)

    def test_paper_archive_sources_are_shown_in_institution_cards(self):
        self.institution.exam_archive_url = "https://universidade.example.br/provas-anteriores/"
        self.institution.source_checked_at = timezone.localdate()
        self.institution.save(update_fields=["exam_archive_url", "source_checked_at"])

        response = self.client.get(reverse("admissions:papers"))

        self.assertContains(response, "Acervos oficiais de provas anteriores")
        self.assertContains(response, self.institution.name)
        self.assertContains(response, self.institution.exam_archive_url)
        self.assertContains(response, "Acessar provas anteriores")

        answer_keys_response = self.client.get(reverse("admissions:answer_keys"))

        self.assertContains(answer_keys_response, self.institution.name)
        self.assertContains(answer_keys_response, self.institution.exam_archive_url)

    def test_comparison_keeps_selected_order_and_limits_to_three(self):
        exams = [
            EntranceExam.objects.create(name=f"Processo {index}", slug=f"processo-{index}", institution=self.institution, is_demo=True)
            for index in range(4)
        ]
        response = self.client.get(reverse("admissions:compare"), {"id": [str(exam.pk) for exam in exams]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["exams"]), 3)
