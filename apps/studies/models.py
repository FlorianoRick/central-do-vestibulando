from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class StudySubject(models.Model):
    name = models.CharField("matéria", max_length=100, unique=True)
    slug = models.SlugField("identificador", unique=True)
    description = models.TextField("descrição", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "matéria"
        verbose_name_plural = "matérias"

    def __str__(self):
        return self.name


class StudyMaterial(models.Model):
    class MaterialType(models.TextChoices):
        SUMMARY = "summary", "Resumo"
        THEORY = "theory", "Conteúdo teórico"
        EXERCISE = "exercise", "Exercício"
        MIND_MAP = "mind_map", "Mapa mental"
        TIP = "tip", "Dica de estudo"
        OTHER = "other", "Outro material"

    subject = models.ForeignKey(StudySubject, on_delete=models.CASCADE, related_name="materials", verbose_name="matéria")
    title = models.CharField("título", max_length=180)
    slug = models.SlugField("identificador", unique=True)
    summary = models.CharField("resumo", max_length=300, blank=True)
    content = models.TextField("conteúdo", blank=True)
    material_type = models.CharField("tipo", max_length=20, choices=MaterialType.choices, default=MaterialType.SUMMARY)
    attachment = models.FileField("arquivo", upload_to="materiais/", blank=True)
    source_url = models.URLField("fonte", blank=True)
    is_official = models.BooleanField("material oficial", default=False)
    is_demo = models.BooleanField("conteúdo demonstrativo", default=False)
    is_published = models.BooleanField("publicado", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["subject__name", "title"]
        verbose_name = "material de estudo"
        verbose_name_plural = "materiais de estudo"

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_official and not self.source_url:
            raise ValidationError({"source_url": "Informe a fonte oficial do material."})


class StudyPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="study_plans", verbose_name="estudante")
    title = models.CharField("nome do plano", max_length=140, default="Meu plano de estudos")
    target_exams = models.ManyToManyField("admissions.EntranceExam", blank=True, related_name="study_plans", verbose_name="vestibulares-alvo")
    subjects = models.ManyToManyField(StudySubject, blank=True, related_name="study_plans", verbose_name="matérias")
    weekly_hours = models.PositiveSmallIntegerField("horas disponíveis por semana", default=7)
    daily_goal_minutes = models.PositiveSmallIntegerField("meta diária em minutos", default=60)
    notes = models.TextField("observações", blank=True)
    is_active = models.BooleanField("plano ativo", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "plano de estudos"
        verbose_name_plural = "planos de estudos"

    def __str__(self):
        return self.title


class StudySession(models.Model):
    class SessionStatus(models.TextChoices):
        PLANNED = "planned", "Planejada"
        COMPLETED = "completed", "Concluída"
        REVIEW = "review", "Revisão"

    plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name="sessions", verbose_name="plano")
    subject = models.ForeignKey(StudySubject, on_delete=models.PROTECT, related_name="sessions", verbose_name="matéria")
    scheduled_for = models.DateField("data")
    duration_minutes = models.PositiveSmallIntegerField("duração em minutos", default=60)
    topic = models.CharField("assunto", max_length=180, blank=True)
    difficult_topic = models.CharField("assunto para revisar", max_length=180, blank=True)
    status = models.CharField("situação", max_length=12, choices=SessionStatus.choices, default=SessionStatus.PLANNED)
    completed_at = models.DateTimeField("concluída em", null=True, blank=True)
    notes = models.TextField("observações", blank=True)

    class Meta:
        ordering = ["scheduled_for", "subject__name"]
        verbose_name = "sessão de estudo"
        verbose_name_plural = "sessões de estudo"

    def __str__(self):
        return f"{self.subject} — {self.scheduled_for:%d/%m/%Y}"


class MockExamResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mock_exam_results", verbose_name="estudante")
    exam = models.ForeignKey("admissions.EntranceExam", on_delete=models.SET_NULL, null=True, blank=True, related_name="mock_results", verbose_name="processo seletivo")
    title = models.CharField("simulado", max_length=180)
    taken_on = models.DateField("realizado em")
    score = models.DecimalField("pontuação", max_digits=7, decimal_places=2)
    maximum_score = models.DecimalField("pontuação máxima", max_digits=7, decimal_places=2, null=True, blank=True)
    notes = models.TextField("observações", blank=True)

    class Meta:
        ordering = ["-taken_on"]
        verbose_name = "resultado de simulado"
        verbose_name_plural = "resultados de simulados"

    def __str__(self):
        return self.title
