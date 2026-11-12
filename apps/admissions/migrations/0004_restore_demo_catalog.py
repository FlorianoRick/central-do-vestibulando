from django.db import migrations


DEMO_PROCESSES = (
    ("INEP", "Instituto Nacional de Estudos e Pesquisas Educacionais", "inep", "federal", "ENEM", "enem", "enem-inep"),
    ("USP", "Universidade de São Paulo", "usp", "estadual", "FUVEST — USP", "vestibular", "fuvest-usp-usp"),
    ("UNICAMP", "Universidade Estadual de Campinas", "unicamp", "estadual", "Comvest — UNICAMP", "vestibular", "comvest-unicamp-unicamp"),
    ("UNESP", "Universidade Estadual Paulista", "unesp", "estadual", "Vestibular UNESP", "vestibular", "vestibular-unesp-unesp"),
    ("FATEC", "Faculdades de Tecnologia do Estado de São Paulo", "fatec", "estadual", "Vestibular FATEC", "vestibular", "vestibular-fatec-fatec"),
    ("UNIFESP", "Universidade Federal de São Paulo", "unifesp", "federal", "Ingresso — UNIFESP", "vestibular", "ingresso-unifesp-unifesp"),
    ("UFRGS", "Universidade Federal do Rio Grande do Sul", "ufrgs", "federal", "Vestibular UFRGS", "vestibular", "vestibular-ufrgs-ufrgs"),
    ("UFPR", "Universidade Federal do Paraná", "ufpr", "federal", "Vestibular UFPR", "vestibular", "vestibular-ufpr-ufpr"),
    ("UERJ", "Universidade do Estado do Rio de Janeiro", "uerj", "estadual", "Vestibular UERJ", "vestibular", "vestibular-uerj-uerj"),
    ("UnB", "Universidade de Brasília", "unb", "federal", "Ingresso — UnB", "vestibular", "ingresso-unb-unb"),
    ("IFSP", "Instituto Federal de São Paulo", "ifsp", "instituto", "Processo seletivo — IFSP", "vestibular", "processo-seletivo-ifsp-ifsp"),
    ("SISU", "Sistema de Seleção Unificada", "sisu", "nacional", "SISU", "sisu", "sisu-sisu"),
    ("ProUni", "Programa Universidade para Todos", "prouni", "nacional", "ProUni", "prouni", "prouni-prouni"),
    ("FIES", "Fundo de Financiamento Estudantil", "fies", "nacional", "FIES", "fies", "fies-fies"),
)


def restore_demo_catalog(apps, schema_editor):
    database = schema_editor.connection.alias
    Institution = apps.get_model("admissions", "Institution")
    EntranceExam = apps.get_model("admissions", "EntranceExam")

    for acronym, name, slug, institution_type, exam_name, process_type, exam_slug in DEMO_PROCESSES:
        institution, _created = Institution.objects.using(database).get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "acronym": acronym,
                "institution_type": institution_type,
                "description": "Registro demonstrativo sem calendário ou link oficial cadastrado.",
                "is_demo": True,
            },
        )
        EntranceExam.objects.using(database).get_or_create(
            slug=exam_slug,
            defaults={
                "name": exam_name,
                "institution_id": institution.pk,
                "process_type": process_type,
                "description": "Exemplo de cadastro para demonstrar o catálogo. Consulte os canais oficiais para informações atualizadas.",
                "verification_status": "required",
                "is_demo": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("admissions", "0003_keep_fatec_and_unesp"),
    ]

    operations = [
        migrations.RunPython(restore_demo_catalog),
    ]
