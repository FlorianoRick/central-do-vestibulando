from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("conta/", include("apps.accounts.urls")),
    path("vestibulares/", include("apps.admissions.urls")),
    path("materiais/", include("apps.studies.urls")),
    path("noticias/", include("apps.news.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
