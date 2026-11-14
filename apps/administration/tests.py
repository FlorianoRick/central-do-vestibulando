from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class AdministrationAccessTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="gestor",
            email="gestor@example.com",
            password="Senha-segura-123!",
        )
        self.student = User.objects.create_user(
            username="estudante",
            email="estudante@example.com",
            password="Senha-segura-123!",
        )

    def test_dashboard_requires_active_staff(self):
        response = self.client.get(reverse("administration:dashboard"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("administration:dashboard")).status_code, 302)

        self.client.force_login(self.admin)
        response = self.client.get(reverse("administration:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestão interna")
        self.assertContains(response, "Acervo de provas")

    def test_only_superusers_can_manage_roles_and_changes_are_logged(self):
        roles_url = reverse("administration:user_roles")
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(roles_url).status_code, 302)

        self.client.force_login(self.admin)
        response = self.client.post(
            roles_url,
            {
                "user_id": self.student.pk,
                "is_active": "on",
                "is_staff": "on",
            },
        )
        self.assertRedirects(response, roles_url)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_staff)
        self.assertFalse(self.student.is_superuser)
        self.assertTrue(
            LogEntry.objects.filter(
                user=self.admin,
                object_id=str(self.student.pk),
            ).exists()
        )

    def test_last_active_superuser_cannot_remove_own_access(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("administration:user_roles"),
            {
                "user_id": self.admin.pk,
                "is_active": "on",
                "is_staff": "on",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Não é possível remover as próprias permissões administrativas.")
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)
        self.assertTrue(self.admin.is_superuser)
        self.assertFalse(LogEntry.objects.exists())
