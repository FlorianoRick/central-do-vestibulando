from datetime import date

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.admissions.models import EntranceExam, Institution
from apps.news.models import NewsArticle
from apps.studies.models import StudyMaterial, StudySubject


SUBJECTS = {
    "Biologia": "Revise conceitos com esquemas próprios e conecte processos biológicos a exemplos do cotidiano.",
    "Filosofia": "Compare ideias de diferentes autores e registre os conceitos centrais com suas próprias palavras.",
    "Física": "Resolva exercícios mostrando as unidades e as etapas do raciocínio, além do resultado final.",
    "Geografia": "Relacione mapas, escalas e indicadores a processos sociais, ambientais e econômicos.",
    "História": "Organize os acontecimentos em linhas do tempo e identifique causas, agentes e consequências.",
    "Inglês": "Leia textos curtos com frequência e use o contexto para inferir palavras desconhecidas.",
    "Literatura": "Observe narrador, linguagem e contexto da obra antes de elaborar uma interpretação.",
    "Matemática": "Pratique um tipo de problema por vez e confira os cálculos com uma estratégia diferente.",
    "Química": "Conecte representações de partículas, equações e fenômenos observáveis.",
    "Sociologia": "Defina os conceitos e use exemplos sociais para comparar perspectivas teóricas.",
    "Língua Portuguesa": "Leia com atenção ao gênero, à intenção comunicativa e às escolhas linguísticas do texto.",
}


EXAMS = [
    (
        "FATEC", "Faculdades de Tecnologia do Estado de São Paulo", "fatec", "estadual",
        "Vestibular FATEC", "vestibular", "https://www.cps.sp.gov.br/fatec/",
        "https://vestibular.fatec.sp.gov.br/", "https://vestibular.fatec.sp.gov.br/provas-gabaritos/",
    ),
    (
        "UNESP", "Universidade Estadual Paulista", "unesp", "estadual",
        "Vestibular UNESP", "vestibular", "https://www.unesp.br/",
        "https://vestibular.unesp.br/", "https://vestibular.unesp.br/portal#!/arquivo/",
    ),
    (
        "UNICAMP", "Universidade Estadual de Campinas", "unicamp", "estadual",
        "Vestibular UNICAMP", "vestibular", "https://www.unicamp.br/",
        "https://www.comvest.unicamp.br/", "https://www.comvest.unicamp.br/vestibulares-anteriores/",
    ),
    (
        "USP", "Universidade de São Paulo", "usp", "estadual",
        "FUVEST — USP", "vestibular", "https://www.usp.br/",
        "https://www.fuvest.br/", "https://www.fuvest.br/acervo-vestibular/",
    ),
    (
        "PUC-SP", "Pontifícia Universidade Católica de São Paulo", "puc-sp", "privada",
        "Vestibular PUC-SP", "vestibular", "https://www.pucsp.br/",
        "https://nucvest.com.br/", "https://nucvest.com.br/processos-anteriores.html",
    ),
]


NEWS = [
    (
        "Guia demonstrativo: como conferir informações de um vestibular",
        "Confira a instituição responsável, a página do edital e a data da última atualização antes de se inscrever.",
        "Use sempre o endereço oficial da instituição e compare datas e regras com o edital publicado. Este guia é um exemplo de conteúdo, não um comunicado institucional.",
    ),
    (
        "Guia demonstrativo: por onde começar a ler um edital",
        "Encontre requisitos, etapas, documentos e canais de atendimento no documento oficial do processo seletivo.",
        "Comece pelo cronograma e pelos requisitos. Depois confira documentos, critérios de isenção, etapas de prova e instruções de matrícula. Este texto é apenas uma orientação geral.",
    ),
    (
        "Guia demonstrativo: organize uma rotina de revisão",
        "Uma rotina possível combina prática, revisão espaçada e tempo para acompanhar as fontes oficiais.",
        "Escolha assuntos específicos para cada sessão, registre dúvidas e retome os pontos difíceis em outro dia. Ajuste a rotina à sua disponibilidade e ao programa oficial escolhido.",
    ),
]


class Command(BaseCommand):
    help = "Cria registros demonstrativos sem datas ou links oficiais."

    def handle(self, *args, **options):
        subjects = {}
        for name, description in SUBJECTS.items():
            subject, _ = StudySubject.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "description": description},
            )
            subjects[name] = subject

        for acronym, name, slug, institution_type, exam_name, process_type, website_url, entrance_url, archive_url in EXAMS:
            institution, _ = Institution.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "acronym": acronym,
                    "institution_type": institution_type,
                    "website_url": website_url,
                    "entrance_url": entrance_url,
                    "exam_archive_url": archive_url,
                    "description": "Consulte o vestibular e o acervo oficial para informações atualizadas.",
                    "source_checked_at": date(2026, 11, 14),
                    "is_demo": False,
                    "is_active": True,
                },
            )
            EntranceExam.objects.get_or_create(
                slug=f"{slugify(exam_name)}-{slug}",
                defaults={
                    "name": exam_name,
                    "institution": institution,
                    "process_type": process_type,
                    "description": "Exemplo de cadastro para demonstrar o catálogo. Consulte os canais oficiais para informações atualizadas.",
                    "verification_status": EntranceExam.VerificationStatus.REQUIRED,
                    "is_demo": True,
                },
            )

        material_count = 0
        for subject_name, tip in SUBJECTS.items():
            subject = subjects[subject_name]
            _, created = StudyMaterial.objects.get_or_create(
                slug=f"guia-inicial-{subject.slug}",
                defaults={
                    "subject": subject,
                    "title": f"Guia inicial de {subject.name}",
                    "summary": tip,
                    "content": f"{tip}\n\nEste conteúdo é demonstrativo e serve como ponto de partida. Consulte o programa oficial do vestibular escolhido para confirmar os assuntos cobrados.",
                    "material_type": StudyMaterial.MaterialType.TIP,
                    "is_demo": True,
                    "is_official": False,
                },
            )
            material_count += int(created)

        article_count = 0
        for index, (title, summary, content) in enumerate(NEWS, start=1):
            _, created = NewsArticle.objects.get_or_create(
                slug=f"guia-demonstrativo-{index}",
                defaults={
                    "title": title,
                    "summary": summary,
                    "content": content,
                    "is_demo": True,
                },
            )
            article_count += int(created)

        self.stdout.write(self.style.SUCCESS(
            f"Dados demonstrativos disponíveis: {EntranceExam.objects.filter(is_demo=True, institution__is_active=True).count()} processos no catálogo ativo, {len(subjects)} matérias, {material_count} materiais e {article_count} guias novos."
        ))
