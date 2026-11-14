import html
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from django.conf import settings
from django.core.management.base import BaseCommand


EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "media",
    "uploads",
    "staticfiles",
    "exports",
}
EXCLUDED_SUFFIXES = {
    ".sqlite",
    ".sqlite3",
    ".db",
    ".pyc",
    ".pyo",
    ".log",
    ".pem",
    ".key",
    ".bak",
    ".dump",
    ".zip",
    ".tar",
    ".gz",
}
DOCUMENTATION_SUFFIXES = {
    ".py",
    ".html",
    ".css",
    ".js",
    ".json",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".sh",
    ".ps1",
    ".bat",
    ".xml",
    ".svg",
}
MAX_DOCUMENTATION_FILE_SIZE = 1_000_000


def _is_excluded(path, root, output_dir):
    relative = path.relative_to(root)
    if any(part.lower() in EXCLUDED_DIRECTORIES for part in relative.parts):
        return True
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    if path.name.lower().startswith(".env.") and path.name.lower() != ".env.example":
        return True
    if path.name.lower() == ".env":
        return True
    resolved_output = output_dir.resolve()
    resolved_path = path.resolve()
    return resolved_output == resolved_path or resolved_output in resolved_path.parents


def _source_files(root, output_dir):
    files = []
    for current, directories, names in os.walk(root):
        directories[:] = sorted(
            name for name in directories
            if name.lower() not in EXCLUDED_DIRECTORIES
        )
        current_path = Path(current)
        for name in names:
            path = current_path / name
            if path.is_file() and not _is_excluded(path, root, output_dir):
                files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix().lower())


def _documentation_html(root, files):
    sections = []
    index = []
    for number, path in enumerate(files, start=1):
        if path.suffix.lower() not in DOCUMENTATION_SUFFIXES:
            continue
        if path.stat().st_size > MAX_DOCUMENTATION_FILE_SIZE:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        relative = path.relative_to(root).as_posix()
        anchor = f"arquivo-{number}"
        escaped_path = html.escape(relative)
        index.append(f'<li><a href="#{anchor}">{escaped_path}</a></li>')
        sections.append(
            f'<section class="source-file" id="{anchor}">'
            f"<h2>{escaped_path}</h2><pre><code>{html.escape(content)}</code></pre>"
            "</section>"
        )
    index_markup = "\n".join(index)
    sections_markup = "\n".join(sections)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Referência do código — Vestibulando</title>
  <style>
    :root {{ color-scheme: dark; font-family: system-ui, sans-serif; background: #101722; color: #dce4ef; }}
    body {{ margin: 0 auto; max-width: 1280px; padding: 28px 20px; }}
    h1, h2 {{ color: #a9c6f6; }}
    a {{ color: #9cc0ff; }}
    nav {{ padding: 18px; border: 1px solid #2d3c50; border-radius: 8px; background: #1b2838; }}
    nav ul {{ columns: 2; padding-left: 22px; }}
    li {{ break-inside: avoid; margin: 5px 0; }}
    .source-file {{ margin: 28px 0; scroll-margin-top: 16px; }}
    pre {{ overflow: auto; padding: 18px; border: 1px solid #2d3c50; border-radius: 8px; background: #0e1520; line-height: 1.5; }}
    code {{ white-space: pre; font: 13px/1.5 ui-monospace, Consolas, monospace; }}
    @media (max-width: 760px) {{ nav ul {{ columns: 1; }} body {{ padding: 18px 12px; }} }}
  </style>
</head>
<body>
  <header><h1>Vestibulando — referência do código</h1>
    <p>Documentação local gerada a partir dos arquivos de código e configuração do projeto.</p>
  </header>
  <nav aria-label="Arquivos incluídos"><h2>Índice</h2><ul>{index_markup}</ul></nav>
  <main>{sections_markup}</main>
</body>
</html>
"""


class Command(BaseCommand):
    help = "Gera um ZIP do código e uma referência HTML sem dados locais nem segredos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=settings.BASE_DIR / "exports",
            help="Pasta de saída (padrão: exports/).",
        )

    def handle(self, *args, **options):
        root = Path(settings.BASE_DIR).resolve()
        output_dir = options["output_dir"].expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        files = _source_files(root, output_dir)
        if not files:
            self.stderr.write(self.style.ERROR("Nenhum arquivo de código foi encontrado para exportar."))
            return

        zip_path = output_dir / "vestibulando-source.zip"
        html_path = output_dir / "source-reference.html"
        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.relative_to(root).as_posix())
        html_path.write_text(_documentation_html(root, files), encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(
                f"Pacote gerado com {len(files)} arquivos: {zip_path} e {html_path}"
            )
        )
