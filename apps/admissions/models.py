from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Institution(models.Model):
    class InstitutionType(models.TextChoices):
        FEDERAL = "federal", "Universidade federal"
        STATE = "estadual", "Universidade estadual"
        MUNICIPAL = "municipal", "Universidade municipal"
        PRIVATE = "privada", "Instituição privada"
        INSTITUTE = "instituto", "Instituto federal"
        NATIONAL = "nacional", "Processo nacional"
        OTHER = "outro", "Outra instituição"

    name = models.CharField("nome", max_length=180)
    acronym = models.CharField("sigla", max_length=30, blank=True)
    slug = models.SlugField("identificador", unique=True)
    institution_type = models.CharField("tipo", max_length=20, choices=InstitutionType.choices, default=InstitutionType.OTHER)
    state = models.CharField("UF", max_length=2, blank=True)
    city = models.CharField("cidade", max_length=100, blank=True)
    region = models.CharField("região", max_length=20, blank=True)
    website_url = models.URLField("site oficial", blank=True)
    description = models.TextField("descrição", blank=True)
    is_demo = models.BooleanField("cadastro demonstrativo", default=False)
    is_active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "instituição"
        verbose_name_plural = "instituições"

    def __str__(self):
        return self.acronym or self.name


class Course(models.Model):
    name = models.CharField("curso", max_length=120, unique=True)
    slug = models.SlugField("identificador", unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "curso"
        verbose_name_plural = "cursos"

    def __str__(self):
        return self.name


class EntranceExam(models.Model):
    class ProcessType(models.TextChoices):
        VESTIBULAR = "vestibular", "Vestibular"
        ENEM = "enem", "ENEM"
        SISU = "sisu", "SISU"
        PROUNI = "prouni", "ProUni"
        FIES = "fies", "FIES"
        TRANSFER = "transferencia", "Transferência"
        OTHER = "outro", "Outro processo seletivo"

    class VerificationStatus(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmado em fonte oficial"
        AWAITING = "awaiting", "Aguardando publicação"
        REVIEW = "review", "Em análise"
        CLOSED = "closed", "Inscrições encerradas"
        UPDATED = "updated", "Informação atualizada"
        REQUIRED = "required", "Verificação necessária"

    name = models.CharField("nome do processo", max_length=180)
    slug = models.SlugField("identificador", unique=True)
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT, related_name="exams", verbose_name="instituição")
    process_type = models.CharField("tipo de processo", max_length=20, choices=ProcessType.choices, default=ProcessType.VESTIBULAR)
    description = models.TextField("descrição", blank=True)
    courses = models.ManyToManyField(Course, blank=True, related_name="exams", verbose_name="cursos")
    syllabus_subjects = models.ManyToManyField("studies.StudySubject", blank=True, related_name="exams", verbose_name="matérias do programa")
    syllabus_topics = models.TextField("tópicos do programa", blank=True, help_text="Informe os tópicos e a fonte que os confirma.")
    exam_format = models.CharField("formato da prova", max_length=180, blank=True)
    admission_criteria = models.TextField("critérios de ingresso", blank=True)
    exam_phases = models.PositiveSmallIntegerField("fases", null=True, blank=True)
    positions = models.PositiveIntegerField("vagas", null=True, blank=True)
    fee_amount = models.DecimalField("taxa de inscrição", max_digits=8, decimal_places=2, null=True, blank=True)
    fee_exemption = models.CharField("isenção da taxa", max_length=240, blank=True)
    registration_opens_at = models.DateTimeField("início das inscrições", null=True, blank=True)
    registration_closes_at = models.DateTimeField("fim das inscrições", null=True, blank=True)
    exam_at = models.DateTimeField("data da prova", null=True, blank=True)
    result_at = models.DateTimeField("divulgação do resultado", null=True, blank=True)
    enrollment_starts_at = models.DateTimeField("início das matrículas", null=True, blank=True)
    enrollment_ends_at = models.DateTimeField("fim das matrículas", null=True, blank=True)
    registration_url = models.URLField("link de inscrição", blank=True)
    source_url = models.URLField("fonte oficial", blank=True)
    candidate_guide_url = models.URLField("manual do candidato", blank=True)
    announcement_file = models.FileField("edital", upload_to="editais/", blank=True)
    candidate_guide_file = models.FileField("arquivo do manual", upload_to="manuais/", blank=True)
    verification_status = models.CharField("situação da verificação", max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.REQUIRED)
    verified_at = models.DateTimeField("verificado em", null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_exams", verbose_name="responsável pela verificação")
    is_demo = models.BooleanField("cadastro demonstrativo", default=False)
    is_active = models.BooleanField("ativo", default=True)
    notes = models.TextField("observações", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["institution__name", "name"]
        indexes = [models.Index(fields=["verification_status", "registration_closes_at"])]
        verbose_name = "vestibular ou processo seletivo"
        verbose_name_plural = "vestibulares e processos seletivos"

    def __str__(self):
        return f"{self.name} — {self.institution}"

    def clean(self):
        if self.verification_status == self.VerificationStatus.CONFIRMED and (self.is_demo or not self.source_url):
            raise ValidationError({"source_url": "Um processo só pode ser confirmado com uma fonte oficial e sem marcação de demonstração."})
        if self.registration_opens_at and self.registration_closes_at and self.registration_closes_at < self.registration_opens_at:
            raise ValidationError({"registration_closes_at": "O encerramento não pode ocorrer antes da abertura das inscrições."})

    @property
    def officially_verified(self):
        return (
            self.verification_status == self.VerificationStatus.CONFIRMED
            and not self.is_demo
            and bool(self.source_url)
        )

    @property
    def registration_is_open(self):
        now = timezone.now()
        return (
            self.officially_verified
            and self.registration_opens_at is not None
            and self.registration_closes_at is not None
            and self.registration_opens_at <= now <= self.registration_closes_at
        )


class CalendarEvent(models.Model):
    class EventType(models.TextChoices):
        REGISTRATION_OPEN = "registration_open", "Abertura das inscrições"
        REGISTRATION_CLOSE = "registration_close", "Encerramento das inscrições"
        FEE_EXEMPTION = "fee_exemption", "Prazo de isenção"
        LOCATION = "location", "Local de prova"
        EXAM = "exam", "Prova"
        ANSWER_KEY = "answer_key", "Gabarito"
        RESULT = "result", "Resultado"
        APPEAL = "appeal", "Recurso"
        ENROLLMENT = "enrollment", "Matrícula"
        OTHER = "other", "Outro prazo"

    exam = models.ForeignKey(EntranceExam, on_delete=models.CASCADE, related_name="events", verbose_name="processo seletivo")
    title = models.CharField("título", max_length=180)
    event_type = models.CharField("tipo de evento", max_length=24, choices=EventType.choices, default=EventType.OTHER)
    starts_at = models.DateTimeField("data e hora")
    ends_at = models.DateTimeField("término", null=True, blank=True)
    source_url = models.URLField("fonte oficial", blank=True)
    verification_status = models.CharField("situação da verificação", max_length=20, choices=EntranceExam.VerificationStatus.choices, default=EntranceExam.VerificationStatus.REQUIRED)
    is_demo = models.BooleanField("cadastro demonstrativo", default=False)
    notes = models.TextField("observações", blank=True)

    class Meta:
        ordering = ["starts_at", "title"]
        indexes = [models.Index(fields=["starts_at", "verification_status"])]
        verbose_name = "evento do calendário"
        verbose_name_plural = "eventos do calendário"

    def __str__(self):
        return f"{self.title} — {self.exam}"

    def clean(self):
        if self.verification_status == EntranceExam.VerificationStatus.CONFIRMED:
            if self.is_demo or not (self.source_url or self.exam.source_url):
                raise ValidationError({"source_url": "Um prazo só pode ser confirmado com uma fonte oficial."})


class ExamDocument(models.Model):
    class DocumentType(models.TextChoices):
        ANNOUNCEMENT = "announcement", "Edital"
        GUIDE = "guide", "Manual do candidato"
        SYLLABUS = "syllabus", "Programa de matérias"
        OTHER = "other", "Outro documento"

    exam = models.ForeignKey(EntranceExam, on_delete=models.CASCADE, related_name="documents", verbose_name="processo seletivo")
    title = models.CharField("título", max_length=180)
    document_type = models.CharField("tipo", max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER)
    file = models.FileField("arquivo", upload_to="documentos/", blank=True)
    external_url = models.URLField("link do documento", blank=True)
    source_url = models.URLField("fonte oficial", blank=True)
    is_official = models.BooleanField("documento oficial", default=False)
    is_demo = models.BooleanField("cadastro demonstrativo", default=False)
    added_at = models.DateTimeField("adicionado em", auto_now_add=True)

    class Meta:
        ordering = ["document_type", "title"]
        verbose_name = "documento de vestibular"
        verbose_name_plural = "documentos de vestibular"

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_official and not self.source_url:
            raise ValidationError({"source_url": "Informe a fonte oficial do documento."})


class ExamPaper(models.Model):
    class PaperType(models.TextChoices):
        FIRST_PHASE = "first", "Primeira fase"
        SECOND_PHASE = "second", "Segunda fase"
        UNIQUE = "unique", "Fase única"
        ESSAY = "essay", "Redação"
        OTHER = "other", "Outro tipo"

    exam = models.ForeignKey(EntranceExam, on_delete=models.CASCADE, related_name="papers", verbose_name="processo seletivo")
    title = models.CharField("título", max_length=180)
    year = models.PositiveSmallIntegerField("ano", null=True, blank=True)
    phase = models.CharField("fase", max_length=30, blank=True)
    paper_type = models.CharField("tipo de prova", max_length=12, choices=PaperType.choices, default=PaperType.OTHER)
    subject = models.ForeignKey("studies.StudySubject", on_delete=models.SET_NULL, null=True, blank=True, related_name="papers", verbose_name="matéria")
    paper_file = models.FileField("arquivo da prova", upload_to="provas/", blank=True)
    paper_url = models.URLField("link da prova", blank=True)
    answer_key_file = models.FileField("arquivo do gabarito", upload_to="gabaritos/", blank=True)
    answer_key_url = models.URLField("link do gabarito", blank=True)
    solution_url = models.URLField("resolução comentada", blank=True)
    questions_count = models.PositiveSmallIntegerField("número de questões", null=True, blank=True)
    source_url = models.URLField("fonte", blank=True)
    is_official = models.BooleanField("fonte oficial", default=False)
    is_demo = models.BooleanField("cadastro demonstrativo", default=False)
    notes = models.TextField("observações", blank=True)

    class Meta:
        ordering = ["-year", "exam__institution__name", "title"]
        indexes = [models.Index(fields=["year", "paper_type"])]
        verbose_name = "prova anterior"
        verbose_name_plural = "provas anteriores e gabaritos"

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_official and not self.source_url:
            raise ValidationError({"source_url": "Informe a fonte oficial da prova ou do gabarito."})


class ExamUpdateHistory(models.Model):
    exam = models.ForeignKey(EntranceExam, on_delete=models.CASCADE, related_name="history", verbose_name="processo seletivo")
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="alterado por")
    changed_at = models.DateTimeField("alterado em", auto_now_add=True)
    changes = models.JSONField("alterações", default=dict)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "histórico de atualização"
        verbose_name_plural = "históricos de atualização"

    def __str__(self):
        return f"{self.exam} — {self.changed_at:%d/%m/%Y %H:%M}"


class ReviewQueueItem(models.Model):
    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Aguardando análise"
        ACCEPTED = "accepted", "Validado"
        REJECTED = "rejected", "Descartado"

    exam = models.ForeignKey(EntranceExam, on_delete=models.CASCADE, null=True, blank=True, related_name="review_items", verbose_name="processo seletivo")
    title = models.CharField("resumo da alteração", max_length=180)
    candidate_url = models.URLField("fonte encontrada", blank=True)
    discovered_at = models.DateTimeField("identificado em", auto_now_add=True)
    status = models.CharField("situação", max_length=12, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    notes = models.TextField("observações da revisão", blank=True)

    class Meta:
        ordering = ["status", "-discovered_at"]
        verbose_name = "item para revisão"
        verbose_name_plural = "itens para revisão"

    def __str__(self):
        return self.title
