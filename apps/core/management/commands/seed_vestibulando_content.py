from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.admissions.models import Institution
from apps.news.models import NewsArticle
from apps.studies.models import StudyResource, StudySubject


SOURCE_NAME = "Toda Matéria"
LEVEL = "Conteúdo de Ensino Médio para FATEC, UNESP, UNICAMP, USP e PUC"
CHECKED_AT = date(2026, 11, 14)

RESOURCES = {
    "Biologia": (
        "Genética: resumo e conceitos básicos",
        "Revise hereditariedade e conceitos fundamentais de genética.",
        "https://www.todamateria.com.br/introducao-a-genetica/",
    ),
    "Filosofia": (
        "O que é Filosofia?",
        "Conheça os principais temas e o papel da reflexão filosófica.",
        "https://www.todamateria.com.br/o-que-e-filosofia/",
    ),
    "Física": (
        "Leis de Newton",
        "Estude os princípios fundamentais usados para analisar o movimento.",
        "https://www.todamateria.com.br/leis-de-newton/",
    ),
    "Geografia": (
        "Climas do Brasil",
        "Compare os principais tipos climáticos e sua distribuição no território.",
        "https://www.todamateria.com.br/climas-do-brasil/",
    ),
    "História": (
        "Revolução Industrial",
        "Revise as transformações tecnológicas, sociais e econômicas do processo.",
        "https://www.todamateria.com.br/revolucao-industrial/",
    ),
    "Inglês": (
        "Simple Present",
        "Pratique usos e estruturas do presente simples em inglês.",
        "https://www.todamateria.com.br/simple-present/",
    ),
    "Literatura": (
        "Modernismo no Brasil",
        "Conheça características e contexto do movimento modernista brasileiro.",
        "https://www.todamateria.com.br/modernismo-no-brasil/",
    ),
    "Matemática": (
        "Teorema de Pitágoras",
        "Revise a relação entre os lados de um triângulo retângulo.",
        "https://www.todamateria.com.br/teorema-de-pitagoras/",
    ),
    "Química": (
        "Ligações Químicas",
        "Estude ligações iônicas, covalentes e metálicas.",
        "https://www.todamateria.com.br/ligacoes-quimicas/",
    ),
    "Sociologia": (
        "Desigualdade Social",
        "Analise causas, consequências e exemplos de desigualdade social.",
        "https://www.todamateria.com.br/desigualdade-social/",
    ),
    "Língua Portuguesa": (
        "Classes de palavras",
        "Revise as classes gramaticais e suas funções nos textos.",
        "https://www.todamateria.com.br/classes-de-palavras/",
    ),
}

NEWS = (
    {
        "slug": "unicamp-convocados-segunda-fase-vestibular-2027",
        "title": "Unicamp divulga convocados para a segunda fase do Vestibular 2027",
        "summary": "A lista de convocados e as orientações para a próxima etapa devem ser consultadas nos canais oficiais da Comvest.",
        "content": (
            "A Comvest publicou a relação de pessoas convocadas para a segunda fase do Vestibular "
            "Unicamp 2027. Consulte a página oficial para conferir a lista, as orientações e os "
            "documentos relacionados ao processo seletivo."
        ),
        "source_name": "Comvest — Unicamp",
        "source_url": "https://www.comvest.unicamp.br/ingresso-2027/vestibular-2027/",
        "article_url": "https://www.comvest.unicamp.br/ingresso-2027/vestibular-2027/lista-de-aprovados-na-primeira-fase-vestibular-2027/",
        "published_at": datetime(2026, 11, 13, 12, 0),
        "category": NewsArticle.Category.VESTIBULAR,
        "is_featured": True,
    },
    {
        "slug": "fuvest-notas-de-corte-vestibular-2027",
        "title": "Fuvest divulga notas de corte da primeira fase do Vestibular 2027",
        "summary": "A publicação reúne as notas de corte por curso; confirme os dados e comunicados nos canais oficiais da Fuvest.",
        "content": (
            "A Fuvest divulgou as notas de corte da primeira fase do Vestibular 2027. Os valores "
            "variam conforme a carreira. Confira a publicação e eventuais atualizações diretamente "
            "na fonte responsável pelo processo seletivo."
        ),
        "source_name": "G1",
        "source_url": "https://g1.globo.com/sp/sao-paulo/noticia/2026/11/12/nota-de-corte-fuvest-2027-1a-fase.ghtml",
        "article_url": "https://g1.globo.com/sp/sao-paulo/noticia/2026/11/12/nota-de-corte-fuvest-2027-1a-fase.ghtml",
        "published_at": datetime(2026, 11, 12, 12, 0),
        "category": NewsArticle.Category.VESTIBULAR,
        "is_featured": True,
    },
    {
        "slug": "unesp-enem-2027-pedidos-isencao",
        "title": "Unesp-Enem 2027: pedidos de isenção começam em 16 de novembro",
        "summary": "Confira as orientações sobre o pedido de isenção e confirme o prazo no canal oficial do processo.",
        "content": (
            "O processo Unesp-Enem 2027 prevê o início dos pedidos de isenção em 16 de novembro. "
            "Como prazos e requisitos podem ser atualizados, consulte o edital e os canais oficiais "
            "antes de fazer a solicitação."
        ),
        "source_name": "Curso Objetivo — canal de notícias",
        "source_url": "https://curso-objetivo.br/vestibular/ultimas-noticias.aspx",
        "article_url": "https://curso-objetivo.br/vestibular/ultimas-noticias.aspx",
        "published_at": datetime(2026, 11, 13, 12, 0),
        "category": NewsArticle.Category.EDITAL,
        "is_featured": False,
    },
)


class Command(BaseCommand):
    help = "Carrega recursos e notícias iniciais com fontes e revisão registradas."

    def handle(self, *args, **options):
        created_resources = 0
        missing_subjects = []
        for subject_name, (title, description, source_url) in RESOURCES.items():
            subject = StudySubject.objects.filter(name=subject_name, is_active=True).first()
            if subject is None:
                missing_subjects.append(subject_name)
                continue
            _, created = StudyResource.objects.get_or_create(
                subject=subject,
                source_url=source_url,
                defaults={
                    "title": title,
                    "description": description,
                    "source_name": SOURCE_NAME,
                    "vestibular_level": LEVEL,
                    "last_checked_at": CHECKED_AT,
                    "is_published": True,
                    "position": 1,
                },
            )
            created_resources += int(created)

        created_news = 0
        institutions = {
            institution.acronym: institution
            for institution in Institution.objects.filter(
                acronym__in=("UNICAMP", "USP", "UNESP"),
                is_active=True,
                is_demo=False,
            )
        }
        institution_by_slug = {
            institution.slug: institution
            for institution in institutions.values()
        }
        source_institution_slugs = {
            "unicamp": "unicamp",
            "fuvest": "usp",
            "unesp": "unesp",
        }
        for article in NEWS:
            institution = institution_by_slug.get(
                source_institution_slugs[article["slug"].split("-")[0]]
            )
            _, created = NewsArticle.objects.get_or_create(
                slug=article["slug"],
                defaults={
                    **article,
                    "institution": institution,
                    "source_checked_at": CHECKED_AT,
                    "review_status": NewsArticle.ReviewStatus.VERIFIED,
                    "is_demo": False,
                    "is_published": True,
                    "published_at": timezone.make_aware(article["published_at"]),
                },
            )
            created_news += int(created)

        if missing_subjects:
            self.stderr.write(
                self.style.ERROR(
                    "Matérias ativas não encontradas: " + ", ".join(missing_subjects)
                )
            )
            return
        self.stdout.write(
            self.style.SUCCESS(
                f"Conteúdo verificado disponível: {created_resources} recursos e "
                f"{created_news} notícias adicionados. As fontes foram revisadas em "
                f"{CHECKED_AT:%d/%m/%Y}."
            )
        )
