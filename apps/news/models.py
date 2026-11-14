from django.core.exceptions import ValidationError
from django.db import models

from apps.core.validators import validate_news_image


class NewsArticle(models.Model):
    class Category(models.TextChoices):
        VESTIBULAR = "vestibular", "Vestibulares"
        EDITAL = "edital", "Editais e comunicados"
        EDUCACAO = "educacao", "Educação"
        ORIENTACAO = "orientacao", "Orientação"
        OUTROS = "outros", "Outros"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Aguardando verificação"
        VERIFIED = "verified", "Fonte verificada"

    title = models.CharField("título", max_length=180)
    slug = models.SlugField("identificador", unique=True)
    summary = models.CharField("resumo", max_length=320)
    content = models.TextField("conteúdo", blank=True)
    institution = models.ForeignKey("admissions.Institution", on_delete=models.SET_NULL, null=True, blank=True, related_name="news", verbose_name="instituição relacionada")
    published_at = models.DateTimeField("publicado em", null=True, blank=True)
    updated_at = models.DateTimeField("atualizado em", null=True, blank=True)
    source_name = models.CharField("nome da fonte", max_length=160, blank=True)
    source_url = models.URLField("fonte", blank=True)
    article_url = models.URLField("link da publicação original", blank=True)
    review_status = models.CharField(
        "situação da revisão",
        max_length=12,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    source_checked_at = models.DateField("fonte conferida em", null=True, blank=True)
    category = models.CharField("categoria", max_length=16, choices=Category.choices, default=Category.VESTIBULAR)
    image = models.ImageField("imagem", upload_to="noticias/", blank=True, validators=[validate_news_image])
    is_featured = models.BooleanField("notícia importante", default=False)
    is_demo = models.BooleanField("conteúdo demonstrativo", default=False)
    is_published = models.BooleanField("publicado", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "title"]
        verbose_name = "notícia ou aviso"
        verbose_name_plural = "notícias e avisos"

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_published and not self.is_demo:
            errors = {}
            if not self.source_url or not self.published_at:
                errors["source_url"] = "Informe a fonte e a data de publicação antes de publicar uma notícia confirmada."
            if self.review_status != self.ReviewStatus.VERIFIED or not self.source_checked_at:
                errors["review_status"] = "Verifique a fonte e registre a data da revisão antes de publicar."
            if errors:
                raise ValidationError(errors)
