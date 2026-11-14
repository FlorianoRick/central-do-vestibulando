from datetime import date

from django.db import migrations


VERIFIED_ON = date(2026, 11, 14)

INSTITUTIONS = {
    "fatec": {
        "website_url": "https://www.cps.sp.gov.br/fatec/",
        "entrance_url": "https://vestibular.fatec.sp.gov.br/",
        "exam_archive_url": "https://vestibular.fatec.sp.gov.br/provas-gabaritos/",
    },
    "unesp": {
        "website_url": "https://www.unesp.br/",
        "entrance_url": "https://vestibular.unesp.br/",
        "exam_archive_url": "https://vestibular.unesp.br/portal#!/arquivo/",
    },
    "unicamp": {
        "website_url": "https://www.unicamp.br/",
        "entrance_url": "https://www.comvest.unicamp.br/",
        "exam_archive_url": "https://www.comvest.unicamp.br/vestibulares-anteriores/",
    },
    "usp": {
        "website_url": "https://www.usp.br/",
        "entrance_url": "https://www.fuvest.br/",
        "exam_archive_url": "https://www.fuvest.br/acervo-vestibular/",
    },
}


def curate_institutions(apps, schema_editor):
    Institution = apps.get_model("admissions", "Institution")
    Institution.objects.exclude(slug__in=(*INSTITUTIONS, "puc-sp")).update(is_active=False)

    for slug, links in INSTITUTIONS.items():
        Institution.objects.filter(slug=slug).update(
            **links,
            is_active=True,
            is_demo=False,
            source_checked_at=VERIFIED_ON,
        )

    Institution.objects.update_or_create(
        slug="puc-sp",
        defaults={
            "name": "Pontifícia Universidade Católica de São Paulo",
            "acronym": "PUC-SP",
            "institution_type": "privada",
            "state": "SP",
            "city": "São Paulo",
            "website_url": "https://www.pucsp.br/",
            "entrance_url": "https://nucvest.com.br/",
            "exam_archive_url": "https://nucvest.com.br/processos-anteriores.html",
            "description": "Vestibular da PUC-SP organizado pelo NUCVEST.",
            "source_checked_at": VERIFIED_ON,
            "is_demo": False,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("admissions", "0005_institution_entrance_url_and_more"),
    ]

    operations = [
        migrations.RunPython(curate_institutions, migrations.RunPython.noop),
    ]
