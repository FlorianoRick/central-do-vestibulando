from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import NewsArticle


def news_list(request):
    articles = NewsArticle.objects.filter(is_published=True).select_related("institution")
    query = request.GET.get("q", "").strip()
    if query:
        articles = articles.filter(Q(title__icontains=query) | Q(summary__icontains=query) | Q(content__icontains=query))
    page_obj = Paginator(articles, 10).get_page(request.GET.get("page"))
    return render(request, "news/news_list.html", {"articles": page_obj.object_list, "page_obj": page_obj, "query": query})


def news_detail(request, slug):
    article = get_object_or_404(NewsArticle.objects.select_related("institution"), slug=slug, is_published=True)
    return render(request, "news/news_detail.html", {"article": article})
