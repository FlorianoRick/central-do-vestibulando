from django.contrib import admin

from .models import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "published_at", "is_demo", "is_published")
    list_filter = ("is_demo", "is_published", "published_at")
    search_fields = ("title", "summary", "content", "source_name")
    prepopulated_fields = {"slug": ("title",)}
