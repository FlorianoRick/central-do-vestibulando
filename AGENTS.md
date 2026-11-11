# Project guidance

- Keep all user-facing text in natural Brazilian Portuguese.
- Use Django, its templates, forms, authentication, ORM, migrations, and admin as the application stack.
- Preserve the structure of the supplied wireframe when changing page layouts.
- Never display a date, fee, vacancy count, exam file, answer key, or registration link as official without a verifiable source and review status.
- Keep demonstration records visibly marked and free of invented dates or official links.
- Avoid new dependencies unless an implemented feature needs them.
- For model changes, create and commit Django migrations. Run `python manage.py check` and the relevant Django tests.
- Do not commit `.env`, local databases, uploaded media, virtual environments, or editor caches.
