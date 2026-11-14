from pathlib import Path

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


MAX_PDF_SIZE = 25 * 1024 * 1024
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def _is_new_upload(upload):
    return bool(upload) and not getattr(upload, "_committed", True)


def validate_pdf_upload(upload):
    if not _is_new_upload(upload):
        return
    if upload.size > MAX_PDF_SIZE:
        raise ValidationError("O arquivo PDF deve ter no máximo 25 MB.")
    if Path(upload.name).suffix.lower() != ".pdf":
        raise ValidationError("Envie um arquivo com extensão PDF.")
    try:
        upload.seek(0)
        signature = upload.read(5)
    except (AttributeError, OSError) as exc:
        raise ValidationError("Não foi possível verificar o arquivo enviado.") from exc
    finally:
        upload.seek(0)
    if signature != b"%PDF-":
        raise ValidationError("O conteúdo enviado não é um documento PDF válido.")


def validate_news_image(upload):
    if not _is_new_upload(upload):
        return
    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    if upload.size > MAX_IMAGE_SIZE:
        raise ValidationError("A imagem deve ter no máximo 5 MB.")
    if Path(upload.name).suffix.lower() not in allowed_extensions:
        raise ValidationError("Use uma imagem PNG, JPEG ou WebP.")
    try:
        upload.seek(0)
        image = Image.open(upload)
        if image.format not in {"PNG", "JPEG", "WEBP"}:
            raise ValidationError("O conteúdo enviado não é uma imagem permitida.")
        if image.width * image.height > 25_000_000:
            raise ValidationError("A imagem excede o limite de resolução permitido.")
        image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as exc:
        raise ValidationError("O arquivo enviado não é uma imagem válida.") from exc
    finally:
        upload.seek(0)
