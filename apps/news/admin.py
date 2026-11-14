from django.contrib import admin

from .models import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "institution",
        "category",
        "published_at",
        "review_status",
        "is_demo",
        "is_published",
    )
    list_filter = ("category", "review_status", "is_demo", "is_published", "published_at")
    search_fields = ("title", "summary", "content", "source_name")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("institution",)
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Conteúdo", {"fields": ("title", "slug", "summary", "content", "category", "image", "is_featured")}),
        ("Fonte e revisão", {"fields": ("source_name", "source_url", "article_url", "review_status", "source_checked_at")}),
        ("Publicação", {"fields": ("institution", "published_at", "updated_at", "is_demo", "is_published")}),
        ("Registro", {"fields": ("created_at",)}),
    )
