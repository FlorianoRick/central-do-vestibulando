from django.apps import apps
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.core.files.utils import validate_file_name
from django.utils.deconstruct import deconstructible
from django.urls import reverse


@deconstructible
class DatabaseAppearanceStorage(Storage):
    """Keep small, validated branding assets in the persistent Django database."""

    def _asset_model(self):
        return apps.get_model("appearance", "SiteAppearanceAsset")

    def _open(self, name, mode="rb"):
        asset = self._asset_model().objects.get(name=name)
        return ContentFile(bytes(asset.content), name=name)

    def _save(self, name, content):
        name = validate_file_name(name, allow_relative_path=True)
        asset_content = b"".join(content.chunks())
        content_type = getattr(content, "content_type", "application/octet-stream")
        self._asset_model().objects.update_or_create(
            name=name,
            defaults={"content": asset_content, "content_type": content_type},
        )
        return name

    def delete(self, name):
        self._asset_model().objects.filter(name=name).delete()

    def exists(self, name):
        return self._asset_model().objects.filter(name=name).exists()

    def size(self, name):
        asset = self._asset_model().objects.only("content").get(name=name)
        return len(asset.content)

    def url(self, name):
        if name.startswith("appearance/logos/"):
            asset_name = "logo"
        elif name.startswith("appearance/favicons/"):
            asset_name = "favicon"
        else:
            raise ValueError("Arquivo não é um recurso de identidade visual.")
        return reverse("appearance_asset", args=[asset_name])
