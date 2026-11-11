from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.admissions.models import EntranceExam, Institution

User = get_user_model()


class AccountFlowTests(TestCase):
    def test_registration_persists_profile_and_hashes_password(self):
        response = self.client.post(reverse("accounts:register"), {
            "full_name": "Ana Estudante",
            "username": "anaestudante",
            "email": "ANA@example.com",
            "city": "Campinas",
            "state": "SP",
            "target_course": "Medicina",
            "password1": "Preparacao-segura-741!",
            "password2": "Preparacao-segura-741!",
        })
        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(username="anaestudante")
        self.assertEqual(user.email, "ana@example.com")
        self.assertTrue(user.check_password("Preparacao-segura-741!"))
        self.assertNotEqual(user.password, "Preparacao-segura-741!")
        self.assertEqual(user.profile.full_name, "Ana Estudante")
        self.assertEqual(user.profile.target_course, "Medicina")

    def test_login_accepts_email_and_session_can_be_remembered(self):
        user = User.objects.create_user(username="aluno", email="aluno@example.com", password="Preparacao-segura-741!")
        response = self.client.post(reverse("accounts:login"), {
            "username": "ALUNO@example.com",
            "password": "Preparacao-segura-741!",
            "remember": "on",
        })
        self.assertRedirects(response, reverse("accounts:account"))
        self.assertEqual(int(self.client.session.get("_auth_user_id")), user.pk)
        self.assertEqual(self.client.session.get_expiry_age(), 60 * 60 * 24 * 14)

    def test_account_is_private(self):
        response = self.client.get(reverse("accounts:account"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:account')}")

    def test_favorite_is_owned_by_authenticated_user(self):
        user = User.objects.create_user(username="aluno", password="Preparacao-segura-741!")
        institution = Institution.objects.create(name="Universidade Exemplo", slug="universidade-exemplo", is_demo=True)
        exam = EntranceExam.objects.create(name="Vestibular exemplo", slug="vestibular-exemplo", institution=institution, is_demo=True)
        self.client.force_login(user)
        response = self.client.post(reverse("accounts:toggle_exam_favorite", args=[exam.pk]))
        self.assertRedirects(response, reverse("admissions:detail", args=[exam.slug]))
        self.assertEqual(user.favorite_exams.count(), 1)
