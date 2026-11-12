from django.db import migrations, models


SUPPORTED_INSTITUTION_SLUGS = ("fatec", "unesp")


def keep_fatec_and_unesp(apps, schema_editor):
    database = schema_editor.connection.alias
    Institution = apps.get_model("admissions", "Institution")
    EntranceExam = apps.get_model("admissions", "EntranceExam")
    NewsArticle = apps.get_model("news", "NewsArticle")

    removed_institution_ids = list(
        Institution.objects.using(database)
        .exclude(
            models.Q(slug__in=SUPPORTED_INSTITUTION_SLUGS)
            | models.Q(acronym__in=("FATEC", "UNESP"))
        )
        .values_list("pk", flat=True)
    )
    if not removed_institution_ids:
        return

    NewsArticle.objects.using(database).filter(
        institution_id__in=removed_institution_ids
    ).delete()
    EntranceExam.objects.using(database).filter(
        institution_id__in=removed_institution_ids
    ).delete()
    Institution.objects.using(database).filter(
        pk__in=removed_institution_ids
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_initial"),
        ("admissions", "0002_initial"),
        ("news", "0001_initial"),
        ("studies", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(keep_fatec_and_unesp),
    ]
