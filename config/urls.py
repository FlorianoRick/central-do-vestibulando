from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from apps.appearance.views import asset as appearance_asset

urlpatterns = [
    path("gestao/", include("apps.administration.urls")),
    path("admin/design/", include("apps.appearance.urls")),
    path("appearance/assets/<str:asset_name>/", appearance_asset, name="appearance_asset"),
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("conta/", include("apps.accounts.urls")),
    path("vestibulares/", include("apps.admissions.urls")),
    path("materiais/", include("apps.studies.urls")),
    path("noticias/", include("apps.news.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
