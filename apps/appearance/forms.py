import json
from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import ClearableFileInput
from django.urls import reverse
from PIL import Image, UnidentifiedImageError

from .models import DENSITY_CSS, FONT_FAMILY_CSS, SHADOW_CSS, SiteAppearance, is_valid_home_section_order


COLOR_FIELDS = {
    "primary_color", "deep_blue", "success_green", "violet", "background_color",
    "surface_color", "text_color", "secondary_text_color", "border_color",
    "strong_border_color", "muted_background_color", "hover_color", "link_color",
    "soft_blue_color", "soft_green_color", "soft_violet_color",
    "header_background_color", "active_navigation_color", "footer_background_color",
    "footer_text_color", "footer_link_color", "card_background_color",
    "input_background_color", "input_border_color", "focus_color",
}
CSS_VARIABLE_FIELDS = {
    "primary_color": "blue", "deep_blue": "deep-blue", "success_green": "green",
    "violet": "violet", "background_color": "background", "surface_color": "surface",
    "text_color": "text", "secondary_text_color": "muted", "border_color": "border",
    "strong_border_color": "border-dark", "muted_background_color": "muted-background",
    "hover_color": "blue-dark", "link_color": "link-color",
    "soft_blue_color": "soft-blue", "soft_green_color": "soft-green",
    "soft_violet_color": "soft-violet", "header_background_color": "header-background",
    "active_navigation_color": "nav-active", "footer_background_color": "footer-background",
    "footer_text_color": "footer-text", "footer_link_color": "footer-link",
    "card_background_color": "card-background", "input_background_color": "input-background",
    "input_border_color": "input-border", "focus_color": "focus-color",
    "font_family": "font-family", "heading_font_family": "heading-font-family",
    "base_font_size": "font-size-base", "h1_font_size": "font-size-h1",
    "h2_font_size": "font-size-h2", "h3_font_size": "font-size-h3",
    "small_font_size": "font-size-small", "button_font_size": "font-size-button",
    "font_weight": "font-weight", "heading_font_weight": "heading-font-weight",
    "button_font_weight": "button-font-weight", "line_height": "line-height",
    "button_border_radius": "button-radius", "button_height": "button-height",
    "button_horizontal_padding": "button-padding-horizontal",
    "card_border_radius": "card-radius", "card_shadow_intensity": "card-shadow",
    "card_border_enabled": "card-border-width",
    "card_padding": "card-padding", "input_border_radius": "input-radius",
    "input_height": "input-height", "header_height": "header-height",
    "navigation_spacing": "navigation-spacing", "logo_width": "logo-width",
    "logo_height": "logo-height", "footer_section_spacing": "footer-section-spacing",
    "content_width": "content-width", "horizontal_spacing": "horizontal-spacing",
    "section_spacing": "section-spacing", "density": "density-scale",
}
class PortugueseClearableFileInput(ClearableFileInput):
    initial_text = "Arquivo atual"
    input_text = "Selecionar outro arquivo"
    clear_checkbox_label = "Restaurar o arquivo original"

    def __init__(self, *args, asset_name=None, **kwargs):
        self.asset_name = asset_name
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.asset_name and context["widget"]["is_initial"]:
            context["widget"]["value"] = CurrentAssetLink(
                value,
                reverse("appearance_asset", args=[self.asset_name]),
            )
        return context


class CurrentAssetLink:
    def __init__(self, file_value, url):
        self.file_value = file_value
        self.url = url

    def __str__(self):
        return Path(str(self.file_value)).name


def _validate_image(upload, field_name, max_size, allowed_formats):
    if not upload:
        return upload
    if upload.size > max_size:
        raise ValidationError(f"O arquivo deve ter no máximo {max_size // 1024} KB.")

    extension = Path(upload.name).suffix.lower()
    expected_formats = {
        ".png": ("PNG", {"image/png"}),
        ".jpg": ("JPEG", {"image/jpeg"}),
        ".jpeg": ("JPEG", {"image/jpeg"}),
        ".webp": ("WEBP", {"image/webp"}),
        ".ico": ("ICO", {"image/vnd.microsoft.icon", "image/x-icon"}),
    }
    expected = expected_formats.get(extension)
    if not expected or expected[0] not in allowed_formats or upload.content_type not in expected[1]:
        raise ValidationError("Use um arquivo PNG, JPEG ou WebP válido." if field_name == "logo" else "Use um arquivo PNG ou ICO válido.")

    try:
        upload.seek(0)
        image = Image.open(upload)
        if image.format != expected[0]:
            raise ValidationError("A extensão do arquivo não corresponde ao conteúdo da imagem.")
        if image.width * image.height > 25_000_000:
            raise ValidationError("A imagem excede o limite de resolução permitido.")
        image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
        raise ValidationError("O arquivo enviado não é uma imagem válida.") from None
    finally:
        upload.seek(0)
    return upload


class SiteAppearanceForm(forms.ModelForm):
    logo = forms.ImageField(
        label="Logotipo",
        required=False,
        widget=PortugueseClearableFileInput(asset_name="logo"),
    )
    favicon = forms.ImageField(
        label="Ícone do site",
        required=False,
        widget=PortugueseClearableFileInput(asset_name="favicon"),
    )

    class Meta:
        model = SiteAppearance
        exclude = (
            "singleton_key",
            "updated_at",
            "last_modified_by",
            "show_home_institutions",
            "draft_settings",
            "draft_saved_at",
            "draft_saved_by",
        )
        widgets = {
            "home_section_order": forms.HiddenInput(),
            "line_height": forms.NumberInput(attrs={"step": "0.05", "min": "1.2", "max": "2.0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            model_field = SiteAppearance._meta.get_field(name)
            default = model_field.get_default()
            if name == "home_section_order":
                default = json.dumps(default)
            elif isinstance(default, bool):
                default = "true" if default else "false"
            elif default is not None:
                default = str(default)
            if name not in {"logo", "favicon"}:
                field.widget.attrs.setdefault("data-default", default or "")
            if name in COLOR_FIELDS:
                field.widget.attrs.update({
                    "class": "color-hex-input",
                    "maxlength": "7",
                    "pattern": "#[0-9A-Fa-f]{6}",
                    "inputmode": "text",
                    "data-css-var": CSS_VARIABLE_FIELDS[name],
                })
            elif name in CSS_VARIABLE_FIELDS:
                field.widget.attrs["data-css-var"] = CSS_VARIABLE_FIELDS[name]
                if name in {"font_family", "heading_font_family"}:
                    field.widget.attrs["data-css-map"] = json.dumps(FONT_FAMILY_CSS)
                elif name == "card_shadow_intensity":
                    field.widget.attrs["data-css-map"] = json.dumps(SHADOW_CSS)
                elif name == "density":
                    field.widget.attrs["data-css-map"] = json.dumps(DENSITY_CSS)
                elif name == "card_border_enabled":
                    field.widget.attrs["data-css-map"] = json.dumps({"true": "1px", "false": "0px"})
                elif name in {"font_size_base", "h1_font_size", "h2_font_size", "h3_font_size", "small_font_size", "button_font_size", "button_border_radius", "button_height", "button_horizontal_padding", "card_border_radius", "card_padding", "input_border_radius", "input_height", "header_height", "navigation_spacing", "logo_width", "logo_height", "footer_section_spacing", "content_width", "horizontal_spacing", "section_spacing"}:
                    field.widget.attrs["data-css-unit"] = "px"
            if name in {"logo", "favicon"}:
                field.widget.attrs["class"] = "image-upload"

    def clean_home_section_order(self):
        order = self.cleaned_data["home_section_order"]
        if not is_valid_home_section_order(order):
            raise ValidationError("Organize cada seção inicial uma única vez.")
        return order

    def clean_logo(self):
        return _validate_image(self.cleaned_data.get("logo"), "logo", 2 * 1024 * 1024, {"PNG", "JPEG", "WEBP"})

    def clean_favicon(self):
        return _validate_image(self.cleaned_data.get("favicon"), "favicon", 512 * 1024, {"PNG", "ICO"})

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("logo") and self.files.get("logo-clear"):
            self.add_error("logo", "Escolha uma imagem ou restaure a original, não as duas opções.")
        if cleaned_data.get("favicon") and self.files.get("favicon-clear"):
            self.add_error("favicon", "Escolha uma imagem ou restaure a original, não as duas opções.")
        return cleaned_data
