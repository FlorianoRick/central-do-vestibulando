from django.db import migrations


def restrict_subjects(apps, schema_editor):
    StudySubject = apps.get_model("studies", "StudySubject")
    StudySubject.objects.filter(slug__in=["espanhol", "redacao"]).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ("studies", "0002_studysubject_is_active_studyresource"),
    ]

    operations = [
        migrations.RunPython(restrict_subjects, migrations.RunPython.noop),
    ]
