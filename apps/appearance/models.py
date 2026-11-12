from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from .storage import DatabaseAppearanceStorage


HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message="Informe uma cor hexadecimal no formato #RRGGBB.",
)

HOME_SECTION_CHOICES = (
    ("exam_overview", "Próximas provas e inscrições abertas"),
    ("updates", "Resultados e comunicados"),
    ("featured_exams", "Processos para conhecer"),
    ("institutions", "Instituições"),
)
HOME_SECTION_KEYS = tuple(key for key, _label in HOME_SECTION_CHOICES)

FONT_FAMILY_CHOICES = (
    ("system", "Padrão do sistema"),
    ("arial", "Arial"),
    ("georgia", "Georgia"),
    ("verdana", "Verdana"),
    ("tahoma", "Tahoma"),
    ("trebuchet", "Trebuchet MS"),
)
FONT_FAMILY_CSS = {
    "system": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    "arial": "Arial, Helvetica, sans-serif",
    "georgia": "Georgia, Times New Roman, serif",
    "verdana": "Verdana, Geneva, sans-serif",
    "tahoma": "Tahoma, Geneva, sans-serif",
    "trebuchet": "Trebuchet MS, Arial, sans-serif",
}
SHADOW_CSS = {
    "none": "none",
    "subtle": "0 8px 24px rgba(23, 43, 77, .06)",
    "medium": "0 12px 32px rgba(23, 43, 77, .12)",
    "strong": "0 16px 40px rgba(23, 43, 77, .18)",
}
DENSITY_CSS = {"compact": "0.85", "comfortable": "1", "spacious": "1.18"}


def default_home_section_order():
    return list(HOME_SECTION_KEYS)


def is_valid_home_section_order(order):
    if not isinstance(order, list) or len(order) != len(HOME_SECTION_KEYS):
        return False
    if not all(isinstance(key, str) and key in HOME_SECTION_KEYS for key in order):
        return False
    return set(order) == set(HOME_SECTION_KEYS)


class SiteAppearance(models.Model):
    class Density(models.TextChoices):
        COMPACT = "compact", "Compacta"
        COMFORTABLE = "comfortable", "Confortável"
        SPACIOUS = "spacious", "Espaçosa"

    class ShadowIntensity(models.TextChoices):
        NONE = "none", "Sem sombra"
        SUBTLE = "subtle", "Discreta"
        MEDIUM = "medium", "Média"
        STRONG = "strong", "Forte"

    class Alignment(models.TextChoices):
        LEFT = "left", "À esquerda"
        CENTER = "center", "Centralizada"

    singleton_key = models.PositiveSmallIntegerField(
        "configuração única", primary_key=True, default=1, editable=False
    )

    primary_color = models.CharField("azul principal", max_length=7, default="#2457C5", validators=[HEX_COLOR_VALIDATOR])
    deep_blue = models.CharField("azul escuro", max_length=7, default="#172B4D", validators=[HEX_COLOR_VALIDATOR])
    success_green = models.CharField("verde de confirmação", max_length=7, default="#18794E", validators=[HEX_COLOR_VALIDATOR])
    violet = models.CharField("violeta", max_length=7, default="#7040B5", validators=[HEX_COLOR_VALIDATOR])
    background_color = models.CharField("fundo da página", max_length=7, default="#F4F7FB", validators=[HEX_COLOR_VALIDATOR])
    surface_color = models.CharField("superfícies", max_length=7, default="#FFFFFF", validators=[HEX_COLOR_VALIDATOR])
    text_color = models.CharField("texto principal", max_length=7, default="#344054", validators=[HEX_COLOR_VALIDATOR])
    secondary_text_color = models.CharField("texto secundário", max_length=7, default="#667085", validators=[HEX_COLOR_VALIDATOR])
    border_color = models.CharField("bordas", max_length=7, default="#DCE3ED", validators=[HEX_COLOR_VALIDATOR])
    strong_border_color = models.CharField("bordas destacadas", max_length=7, default="#C8D2E0", validators=[HEX_COLOR_VALIDATOR])
    muted_background_color = models.CharField("fundo neutro", max_length=7, default="#EEF1F5", validators=[HEX_COLOR_VALIDATOR])
    hover_color = models.CharField("cor ao passar o cursor", max_length=7, default="#1C46A1", validators=[HEX_COLOR_VALIDATOR])
    link_color = models.CharField("links", max_length=7, default="#2457C5", validators=[HEX_COLOR_VALIDATOR])
    soft_blue_color = models.CharField("fundo azul suave", max_length=7, default="#EDF3FF", validators=[HEX_COLOR_VALIDATOR])
    soft_green_color = models.CharField("fundo verde suave", max_length=7, default="#E9F5EF", validators=[HEX_COLOR_VALIDATOR])
    soft_violet_color = models.CharField("fundo violeta suave", max_length=7, default="#F2EDFA", validators=[HEX_COLOR_VALIDATOR])
    header_background_color = models.CharField("fundo do cabeçalho", max_length=7, default="#FFFFFF", validators=[HEX_COLOR_VALIDATOR])
    active_navigation_color = models.CharField("navegação ativa", max_length=7, default="#2457C5", validators=[HEX_COLOR_VALIDATOR])
    footer_background_color = models.CharField("fundo do rodapé", max_length=7, default="#172B4D", validators=[HEX_COLOR_VALIDATOR])
    footer_text_color = models.CharField("texto do rodapé", max_length=7, default="#D7E1F0", validators=[HEX_COLOR_VALIDATOR])
    footer_link_color = models.CharField("links do rodapé", max_length=7, default="#D7E1F0", validators=[HEX_COLOR_VALIDATOR])
    card_background_color = models.CharField("fundo dos cartões", max_length=7, default="#FFFFFF", validators=[HEX_COLOR_VALIDATOR])
    input_background_color = models.CharField("fundo dos campos", max_length=7, default="#FFFFFF", validators=[HEX_COLOR_VALIDATOR])
    input_border_color = models.CharField("borda dos campos", max_length=7, default="#C8D2E0", validators=[HEX_COLOR_VALIDATOR])
    focus_color = models.CharField("realce de foco", max_length=7, default="#2457C5", validators=[HEX_COLOR_VALIDATOR])

    font_family = models.CharField("fonte do texto", max_length=20, choices=FONT_FAMILY_CHOICES, default="system")
    heading_font_family = models.CharField("fonte dos títulos", max_length=20, choices=FONT_FAMILY_CHOICES, default="system")
    base_font_size = models.PositiveSmallIntegerField("tamanho do texto", default=16, validators=[MinValueValidator(14), MaxValueValidator(20)])
    h1_font_size = models.PositiveSmallIntegerField("tamanho do título principal", default=52, validators=[MinValueValidator(28), MaxValueValidator(64)])
    h2_font_size = models.PositiveSmallIntegerField("tamanho dos títulos secundários", default=28, validators=[MinValueValidator(20), MaxValueValidator(44)])
    h3_font_size = models.PositiveSmallIntegerField("tamanho dos subtítulos", default=18, validators=[MinValueValidator(16), MaxValueValidator(32)])
    small_font_size = models.PositiveSmallIntegerField("tamanho dos textos pequenos", default=13, validators=[MinValueValidator(11), MaxValueValidator(16)])
    button_font_size = models.PositiveSmallIntegerField("tamanho do texto dos botões", default=15, validators=[MinValueValidator(12), MaxValueValidator(20)])
    font_weight = models.PositiveSmallIntegerField("peso do texto", default=400, choices=((400, "Normal"), (500, "Médio"), (600, "Seminegrito"), (700, "Negrito")))
    heading_font_weight = models.PositiveSmallIntegerField("peso dos títulos", default=700, choices=((500, "Médio"), (600, "Seminegrito"), (700, "Negrito"), (800, "Extra negrito")))
    button_font_weight = models.PositiveSmallIntegerField("peso dos botões", default=700, choices=((500, "Médio"), (600, "Seminegrito"), (700, "Negrito"), (800, "Extra negrito")))
    line_height = models.DecimalField("altura da linha", max_digits=3, decimal_places=2, default=Decimal("1.55"), validators=[MinValueValidator(Decimal("1.20")), MaxValueValidator(Decimal("2.00"))])

    button_border_radius = models.PositiveSmallIntegerField("arredondamento dos botões", default=9, validators=[MinValueValidator(0), MaxValueValidator(24)])
    button_height = models.PositiveSmallIntegerField("altura dos botões", default=44, validators=[MinValueValidator(36), MaxValueValidator(60)])
    button_horizontal_padding = models.PositiveSmallIntegerField("espaço lateral dos botões", default=18, validators=[MinValueValidator(8), MaxValueValidator(36)])
    card_border_radius = models.PositiveSmallIntegerField("arredondamento dos cartões", default=14, validators=[MinValueValidator(0), MaxValueValidator(32)])
    card_shadow_intensity = models.CharField("sombra dos cartões", max_length=10, choices=ShadowIntensity.choices, default=ShadowIntensity.SUBTLE)
    card_border_enabled = models.BooleanField("exibir borda nos cartões", default=True)
    card_padding = models.PositiveSmallIntegerField("espaço interno dos cartões", default=24, validators=[MinValueValidator(12), MaxValueValidator(48)])
    input_border_radius = models.PositiveSmallIntegerField("arredondamento dos campos", default=8, validators=[MinValueValidator(0), MaxValueValidator(20)])
    input_height = models.PositiveSmallIntegerField("altura dos campos", default=44, validators=[MinValueValidator(36), MaxValueValidator(60)])
    header_height = models.PositiveSmallIntegerField("altura do cabeçalho", default=76, validators=[MinValueValidator(56), MaxValueValidator(110)])
    navigation_spacing = models.PositiveSmallIntegerField("espaço entre links", default=18, validators=[MinValueValidator(8), MaxValueValidator(40)])
    logo_width = models.PositiveSmallIntegerField("largura do logotipo", default=180, validators=[MinValueValidator(80), MaxValueValidator(360)])
    logo_height = models.PositiveSmallIntegerField("altura do logotipo", default=40, validators=[MinValueValidator(24), MaxValueValidator(100)])
    footer_section_spacing = models.PositiveSmallIntegerField("espaço entre colunas do rodapé", default=48, validators=[MinValueValidator(16), MaxValueValidator(96)])

    content_width = models.PositiveSmallIntegerField("largura do conteúdo", default=1180, choices=((1000, "1.000 px"), (1100, "1.100 px"), (1180, "1.180 px"), (1320, "1.320 px"), (1440, "1.440 px")))
    horizontal_spacing = models.PositiveSmallIntegerField("espaçamento horizontal", default=24, choices=((16, "Compacto"), (20, "Reduzido"), (24, "Padrão"), (32, "Amplo")))
    section_spacing = models.PositiveSmallIntegerField("espaço entre seções", default=30, choices=((16, "16 px"), (20, "20 px"), (24, "24 px"), (30, "30 px"), (40, "40 px"), (48, "48 px"), (64, "64 px")))
    density = models.CharField("densidade geral", max_length=16, choices=Density.choices, default=Density.COMFORTABLE)
    hero_alignment = models.CharField("alinhamento do destaque inicial", max_length=10, choices=Alignment.choices, default=Alignment.LEFT)
    show_home_event_panel = models.BooleanField("mostrar painel de prazos confirmados", default=True)
    show_home_upcoming_exams = models.BooleanField("mostrar próximas provas", default=True)
    show_home_open_exams = models.BooleanField("mostrar inscrições abertas", default=True)
    show_home_results = models.BooleanField("mostrar resultados previstos", default=True)
    show_home_news = models.BooleanField("mostrar comunicados recentes", default=True)
    show_home_featured_exams = models.BooleanField("mostrar processos em destaque", default=True)
    show_home_institutions = models.BooleanField("mostrar faixa de instituições", default=True)
    featured_exam_count = models.PositiveSmallIntegerField("quantidade de processos em destaque", default=4, validators=[MinValueValidator(1), MaxValueValidator(8)])
    home_section_order = models.JSONField("ordem das seções iniciais", default=default_home_section_order)

    logo = models.ImageField("logotipo do site", upload_to="appearance/logos/", storage=DatabaseAppearanceStorage(), blank=True)
    favicon = models.ImageField("ícone do site", upload_to="appearance/favicons/", storage=DatabaseAppearanceStorage(), blank=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="appearance_changes", verbose_name="última alteração feita por")

    class Meta:
        verbose_name = "aparência do site"
        verbose_name_plural = "aparência do site"
        constraints = [
            models.CheckConstraint(condition=models.Q(singleton_key=1), name="site_appearance_singleton_key")
        ]

    def __str__(self):
        return "Aparência global do site"

    def clean(self):
        super().clean()
        if not is_valid_home_section_order(self.home_section_order):
            raise ValidationError({"home_section_order": "Selecione cada seção inicial uma única vez."})

    def css_variables(self):
        return {
            "blue": self.primary_color,
            "blue-dark": self.hover_color,
            "deep-blue": self.deep_blue,
            "green": self.success_green,
            "violet": self.violet,
            "background": self.background_color,
            "surface": self.surface_color,
            "text": self.text_color,
            "muted": self.secondary_text_color,
            "border": self.border_color,
            "border-dark": self.strong_border_color,
            "soft-blue": self.soft_blue_color,
            "soft-green": self.soft_green_color,
            "soft-violet": self.soft_violet_color,
            "muted-background": self.muted_background_color,
            "link-color": self.link_color,
            "nav-active": self.active_navigation_color,
            "header-background": self.header_background_color,
            "footer-background": self.footer_background_color,
            "footer-text": self.footer_text_color,
            "footer-link": self.footer_link_color,
            "card-background": self.card_background_color,
            "input-background": self.input_background_color,
            "input-border": self.input_border_color,
            "focus-color": self.focus_color,
            "font-family": FONT_FAMILY_CSS[self.font_family],
            "heading-font-family": FONT_FAMILY_CSS[self.heading_font_family],
            "font-size-base": f"{self.base_font_size}px",
            "font-size-h1": f"{self.h1_font_size}px",
            "font-size-h2": f"{self.h2_font_size}px",
            "font-size-h3": f"{self.h3_font_size}px",
            "font-size-small": f"{self.small_font_size}px",
            "font-size-button": f"{self.button_font_size}px",
            "font-weight": str(self.font_weight),
            "heading-font-weight": str(self.heading_font_weight),
            "button-font-weight": str(self.button_font_weight),
            "line-height": str(self.line_height),
            "button-radius": f"{self.button_border_radius}px",
            "button-height": f"{self.button_height}px",
            "button-padding-horizontal": f"{self.button_horizontal_padding}px",
            "card-radius": f"{self.card_border_radius}px",
            "shadow": SHADOW_CSS[self.card_shadow_intensity],
            "card-shadow": SHADOW_CSS[self.card_shadow_intensity],
            "card-border-width": "1px" if self.card_border_enabled else "0px",
            "card-padding": f"{self.card_padding}px",
            "input-radius": f"{self.input_border_radius}px",
            "input-height": f"{self.input_height}px",
            "header-height": f"{self.header_height}px",
            "navigation-spacing": f"{self.navigation_spacing}px",
            "logo-width": f"{self.logo_width}px",
            "logo-height": f"{self.logo_height}px",
            "footer-section-spacing": f"{self.footer_section_spacing}px",
            "content-width": f"{self.content_width}px",
            "horizontal-spacing": f"{self.horizontal_spacing}px",
            "section-spacing": f"{self.section_spacing}px",
            "density-scale": DENSITY_CSS[self.density],
        }


class SiteAppearanceHistory(models.Model):
    appearance = models.ForeignKey(SiteAppearance, on_delete=models.CASCADE, related_name="history", verbose_name="aparência")
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="appearance_history", verbose_name="alterado por")
    previous_settings = models.JSONField("configuração anterior")
    new_settings = models.JSONField("nova configuração")
    created_at = models.DateTimeField("alterado em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "alteração de aparência"
        verbose_name_plural = "histórico de aparência"

    def __str__(self):
        return f"Aparência atualizada em {self.created_at:%d/%m/%Y %H:%M}"


class SiteAppearanceAsset(models.Model):
    name = models.CharField("identificador do arquivo", max_length=255, primary_key=True)
    content = models.BinaryField("conteúdo")
    content_type = models.CharField("tipo do arquivo", max_length=100)
    created_at = models.DateTimeField("enviado em", auto_now_add=True)

    class Meta:
        verbose_name = "arquivo da identidade visual"
        verbose_name_plural = "arquivos da identidade visual"

    def __str__(self):
        return self.name
