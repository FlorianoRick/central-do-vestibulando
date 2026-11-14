from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import NewsArticle


def _public_articles():
    return NewsArticle.objects.filter(
        is_published=True,
    ).filter(
        Q(is_demo=True)
        | Q(
            review_status=NewsArticle.ReviewStatus.VERIFIED,
            source_checked_at__isnull=False,
            source_url__gt="",
            published_at__isnull=False,
        )
    ).filter(
        Q(published_at__isnull=True) | Q(published_at__lte=timezone.now())
    )


def news_list(request):
    articles = _public_articles().select_related("institution")
    query = request.GET.get("q", "").strip()
    if query:
        articles = articles.filter(Q(title__icontains=query) | Q(summary__icontains=query) | Q(content__icontains=query))
    page_obj = Paginator(articles, 10).get_page(request.GET.get("page"))
    return render(request, "news/news_list.html", {"articles": page_obj.object_list, "page_obj": page_obj, "query": query})


def news_detail(request, slug):
    article = get_object_or_404(
        _public_articles().select_related("institution"),
        slug=slug,
    )
    return render(request, "news/news_detail.html", {"article": article})
