import json
import os
from io import BytesIO, StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management import call_command, CommandError
from django.db import IntegrityError, transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .forms import SiteAppearanceForm
from .models import SiteAppearance, SiteAppearanceAsset, SiteAppearanceHistory
from .services import get_active_appearance


class BootstrapSuperuserTests(TestCase):
    bootstrap_environment = {
        "BOOTSTRAP_SUPERUSER_USERNAME": "first-admin",
        "BOOTSTRAP_SUPERUSER_EMAIL": "first-admin@example.com",
        "BOOTSTRAP_SUPERUSER_PASSWORD": "m8$PzqR4!Vx2#Lk9",
    }

    def test_bootstrap_creates_one_superuser_without_logging_the_password(self):
        output = StringIO()
        with patch.dict(os.environ, self.bootstrap_environment):
            call_command("bootstrap_superuser", stdout=output)
            call_command("bootstrap_superuser", stdout=output)

        user = get_user_model().objects.get(username="first-admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password(self.bootstrap_environment["BOOTSTRAP_SUPERUSER_PASSWORD"]))
        self.assertEqual(get_user_model().objects.filter(is_superuser=True).count(), 1)
        self.assertNotIn(self.bootstrap_environment["BOOTSTRAP_SUPERUSER_PASSWORD"], output.getvalue())

    def test_bootstrap_without_environment_values_is_a_safe_no_op(self):
        with patch.dict(os.environ, {name: "" for name in (
            "BOOTSTRAP_SUPERUSER_USERNAME",
            "BOOTSTRAP_SUPERUSER_EMAIL",
            "BOOTSTRAP_SUPERUSER_PASSWORD",
        )}):
            call_command("bootstrap_superuser", stdout=StringIO())

        self.assertFalse(get_user_model().objects.filter(is_superuser=True).exists())

    def test_partial_bootstrap_configuration_fails_without_creating_an_account(self):
        incomplete_environment = {
            "BOOTSTRAP_SUPERUSER_USERNAME": "first-admin",
            "BOOTSTRAP_SUPERUSER_EMAIL": "",
            "BOOTSTRAP_SUPERUSER_PASSWORD": "",
        }
        with patch.dict(os.environ, incomplete_environment):
            with self.assertRaises(CommandError):
                call_command("bootstrap_superuser", stdout=StringIO())

        self.assertFalse(get_user_model().objects.filter(is_superuser=True).exists())

    def test_bootstrap_adds_admin_without_changing_existing_superuser(self):
        user_model = get_user_model()
        existing_user = user_model.objects.create_superuser(
            username="existing-admin",
            email="existing-admin@example.com",
            password="Different-Password-749!",
        )
        with patch.dict(os.environ, self.bootstrap_environment):
            call_command("bootstrap_superuser", stdout=StringIO())

        existing_user.refresh_from_db()
        self.assertTrue(existing_user.check_password("Different-Password-749!"))
        new_user = user_model.objects.get(username="first-admin")
        self.assertTrue(new_user.is_superuser)
        self.assertTrue(new_user.check_password(self.bootstrap_environment["BOOTSTRAP_SUPERUSER_PASSWORD"]))
        self.assertEqual(user_model.objects.filter(is_superuser=True).count(), 2)


class SiteAppearanceTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.staff_user = self.user_model.objects.create_user(
            username="design-admin",
            password="Seguro-12345!",
            is_staff=True,
        )
        permission = Permission.objects.get(
            content_type__app_label="appearance",
            codename="change_siteappearance",
        )
        self.staff_user.user_permissions.add(permission)
        self.editor_url = reverse("appearance:editor")

    def form_payload(self, appearance=None):
        appearance = appearance or get_active_appearance()
        form = SiteAppearanceForm(instance=appearance)
        payload = {}
        for name in form.fields:
            if name in {"logo", "favicon"}:
                continue
            value = SiteAppearance._meta.get_field(name).get_default()
            if isinstance(value, bool):
                if value:
                    payload[name] = "on"
            elif isinstance(value, list):
                payload[name] = json.dumps(value)
            else:
                payload[name] = str(value)
        return payload

    def png_upload(self, name="marca.png", content_type="image/png"):
        image = Image.new("RGB", (8, 8), color="#2457C5")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)

    def test_default_configuration_is_created_once_and_reaches_public_pages(self):
        appearance = get_active_appearance()
        self.assertEqual(appearance.primary_color, "#285BCB")
        self.assertEqual(get_active_appearance().pk, appearance.pk)
        self.assertEqual(SiteAppearance.objects.count(), 1)

        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "--blue: #285BCB")

    def test_only_staff_with_change_permission_can_open_editor(self):
        anonymous_response = self.client.get(self.editor_url)
        self.assertEqual(anonymous_response.status_code, 302)

        student = self.user_model.objects.create_user(username="student", password="Seguro-12345!")
        self.client.force_login(student)
        self.assertEqual(self.client.get(self.editor_url).status_code, 403)

        self.client.force_login(self.staff_user)
        response = self.client.get(self.editor_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personalização do site")
        self.assertContains(response, "Prévia em tempo real")

    def test_saved_changes_persist_and_create_history(self):
        self.client.force_login(self.staff_user)
        payload = self.form_payload()
        payload["primary_color"] = "#0A1B2C"

        response = self.client.post(self.editor_url, payload)
        self.assertRedirects(response, self.editor_url)

        appearance = get_active_appearance()
        self.assertEqual(appearance.primary_color, "#0A1B2C")
        self.assertEqual(appearance.last_modified_by, self.staff_user)
        history = SiteAppearanceHistory.objects.get()
        self.assertEqual(history.changed_by, self.staff_user)
        self.assertEqual(history.previous_settings["primary_color"], "#285BCB")
        self.assertEqual(history.new_settings["primary_color"], "#0A1B2C")

        home_response = self.client.get(reverse("core:home"))
        self.assertContains(home_response, "--blue: #0A1B2C")

    def test_saving_a_draft_does_not_change_the_published_theme(self):
        self.client.force_login(self.staff_user)
        payload = self.form_payload()
        payload["primary_color"] = "#123456"

        response = self.client.post(self.editor_url, {**payload, "save_draft": "1"})

        self.assertRedirects(response, self.editor_url)
        appearance = get_active_appearance()
        self.assertEqual(appearance.primary_color, "#285BCB")
        self.assertEqual(appearance.draft_settings["primary_color"], "#123456")
        self.assertEqual(appearance.draft_saved_by, self.staff_user)
        self.assertEqual(SiteAppearanceHistory.objects.count(), 0)
        self.assertContains(self.client.get(reverse("core:home")), "--blue: #285BCB")

    def test_publishing_a_saved_draft_activates_and_clears_it(self):
        appearance = get_active_appearance()
        appearance.draft_settings = self.form_payload(appearance)
        appearance.draft_settings["primary_color"] = "#123456"
        appearance.save(update_fields=["draft_settings"])
        self.client.force_login(self.staff_user)

        response = self.client.post(
            self.editor_url,
            {
                **self.form_payload(appearance),
                "primary_color": "#123456",
                "publish_changes": "1",
            },
        )

        self.assertRedirects(response, self.editor_url)
        appearance.refresh_from_db()
        self.assertEqual(appearance.primary_color, "#123456")
        self.assertEqual(appearance.draft_settings, {})

    def test_invalid_color_is_rejected_without_publishing(self):
        self.client.force_login(self.staff_user)
        payload = self.form_payload()
        payload["primary_color"] = "red; color: red"

        response = self.client.post(self.editor_url, payload)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["primary_color"])
        self.assertEqual(get_active_appearance().primary_color, "#285BCB")
        self.assertEqual(SiteAppearanceHistory.objects.count(), 0)

    def test_typography_components_and_home_layout_are_saved(self):
        self.client.force_login(self.staff_user)
        payload = self.form_payload()
        payload.update({
            "font_family": "georgia",
            "button_height": "52",
            "featured_exam_count": "6",
            "hero_alignment": "center",
            "home_section_order": json.dumps(["materials", "updates", "featured_exams", "exam_overview"]),
        })
        payload.pop("show_home_news")

        response = self.client.post(self.editor_url, payload)

        self.assertRedirects(response, self.editor_url)
        appearance = get_active_appearance()
        self.assertEqual(appearance.font_family, "georgia")
        self.assertEqual(appearance.button_height, 52)
        self.assertEqual(appearance.featured_exam_count, 6)
        self.assertEqual(appearance.hero_alignment, "center")
        self.assertEqual(appearance.home_section_order[0], "materials")
        self.assertFalse(appearance.show_home_news)
        home_response = self.client.get(reverse("core:home"))
        self.assertContains(home_response, "Processos seletivos")
        self.assertNotContains(home_response, "Notícias recentes")
        self.assertLess(
            home_response.content.index(b"Resultados previstos"),
            home_response.content.index(b"Processos seletivos"),
        )

    def test_home_section_order_must_contain_each_allowed_section_once(self):
        self.client.force_login(self.staff_user)
        payload = self.form_payload()
        payload["home_section_order"] = json.dumps(["updates", "updates", "featured_exams", "materials"])

        response = self.client.post(self.editor_url, payload)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["home_section_order"])
        self.assertEqual(get_active_appearance().home_section_order[0], "exam_overview")

    def test_home_section_order_rejects_non_string_values(self):
        self.client.force_login(self.staff_user)
        payload = self.form_payload()
        payload["home_section_order"] = json.dumps([{}, "updates", "featured_exams", "materials"])

        response = self.client.post(self.editor_url, payload)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["home_section_order"])

    def test_uploaded_logo_is_served_and_removed_when_restoring_defaults(self):
        self.client.force_login(self.staff_user)
        payload = self.form_payload()
        response = self.client.post(self.editor_url, {**payload, "logo": self.png_upload()})
        self.assertRedirects(response, self.editor_url)

        appearance = get_active_appearance()
        stored_name = appearance.logo.name
        self.assertTrue(appearance.logo.storage.exists(stored_name))
        self.assertTrue(SiteAppearanceAsset.objects.filter(name=stored_name).exists())
        self.assertContains(self.client.get(self.editor_url), 'href="/appearance/assets/logo/"')
        asset_response = self.client.get(reverse("appearance_asset", args=["logo"]))
        self.assertEqual(asset_response.status_code, 200)
        self.assertEqual(asset_response["Content-Type"], "image/png")
        self.assertTrue(b"".join(asset_response.streaming_content).startswith(b"\x89PNG"))

        self.client.post(self.editor_url, {"restore_defaults": "1"})
        appearance.refresh_from_db()
        self.assertFalse(appearance.logo.name)
        self.assertFalse(SiteAppearanceAsset.objects.filter(name=stored_name).exists())

    def test_database_rejects_a_second_global_configuration(self):
        get_active_appearance()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                SiteAppearance.objects.create(singleton_key=2)

    def test_restore_original_appearance_is_confirmable_and_logged(self):
        appearance = get_active_appearance()
        appearance.primary_color = "#123456"
        appearance.save(update_fields=["primary_color"])
        self.client.force_login(self.staff_user)

        response = self.client.post(self.editor_url, {"restore_defaults": "1"})

        self.assertRedirects(response, self.editor_url)
        appearance.refresh_from_db()
        self.assertEqual(appearance.primary_color, "#285BCB")
        self.assertEqual(appearance.last_modified_by, self.staff_user)
        self.assertEqual(SiteAppearanceHistory.objects.count(), 1)

    def test_logo_upload_requires_a_real_supported_image(self):
        appearance = get_active_appearance()
        valid_form = SiteAppearanceForm(
            data=self.form_payload(appearance),
            files={"logo": self.png_upload()},
            instance=appearance,
        )
        self.assertTrue(valid_form.is_valid(), valid_form.errors)

        invalid_form = SiteAppearanceForm(
            data=self.form_payload(appearance),
            files={"logo": SimpleUploadedFile("marca.png", b"nao e imagem", content_type="image/png")},
            instance=appearance,
        )
        self.assertFalse(invalid_form.is_valid())
        self.assertIn("logo", invalid_form.errors)

    def test_asset_route_only_serves_configured_brand_assets(self):
        response = self.client.get(reverse("appearance_asset", args=["logo"]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.get(reverse("appearance_asset", args=["unknown"])).status_code, 404)
