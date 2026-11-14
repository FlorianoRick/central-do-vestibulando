from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import NewsArticle


class NewsReviewTests(TestCase):
    def setUp(self):
        self.verified_article = NewsArticle.objects.create(
            title="Notícia conferida",
            slug="noticia-conferida",
            summary="Resumo com fonte revisada.",
            content="Conteúdo revisado.",
            source_name="Fonte de teste",
            source_url="https://example.com/noticia",
            article_url="https://example.com/noticia",
            published_at=timezone.now(),
            source_checked_at=timezone.localdate(),
            review_status=NewsArticle.ReviewStatus.VERIFIED,
            is_published=True,
        )
        self.pending_article = NewsArticle.objects.create(
            title="Notícia aguardando revisão",
            slug="noticia-aguardando-revisao",
            summary="Este texto não deve ser público.",
            published_at=timezone.now(),
            is_published=True,
        )

    def test_public_news_hides_published_records_without_review(self):
        response = self.client.get(reverse("news:list"))
        self.assertContains(response, self.verified_article.title)
        self.assertNotContains(response, self.pending_article.title)
        self.assertEqual(
            self.client.get(
                reverse("news:detail", args=[self.pending_article.slug])
            ).status_code,
            404,
        )

    def test_publishing_non_demo_news_requires_source_and_review_date(self):
        article = NewsArticle(
            title="Notícia sem revisão",
            slug="noticia-sem-revisao",
            summary="Resumo",
            published_at=timezone.now(),
            is_published=True,
            review_status=NewsArticle.ReviewStatus.PENDING,
        )
        with self.assertRaises(ValidationError) as error:
            article.full_clean()
        self.assertIn("review_status", error.exception.message_dict)
