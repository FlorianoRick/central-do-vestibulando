from django.conf import settings
from django.db import models


BRAZILIAN_STATES = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
    ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
    ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
    ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins"),
]


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile", verbose_name="usuário")
    full_name = models.CharField("nome completo", max_length=160, blank=True)
    city = models.CharField("cidade", max_length=100, blank=True)
    state = models.CharField("estado", max_length=2, choices=BRAZILIAN_STATES, blank=True)
    target_course = models.CharField("curso desejado", max_length=120, blank=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "perfil de estudante"
        verbose_name_plural = "perfis de estudantes"

    def __str__(self):
        return self.full_name or self.user.get_username()


class UserPreferences(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preferences", verbose_name="usuário")
    email_notifications = models.BooleanField("prefere avisos por e-mail", default=False)
    study_reminders = models.BooleanField("lembretes de estudo", default=True)
    deadline_reminders = models.BooleanField("lembretes de prazos", default=True)

    class Meta:
        verbose_name = "preferência de estudante"
        verbose_name_plural = "preferências de estudantes"

    def __str__(self):
        return f"Preferências de {self.user}"


class FavoriteExam(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_exams", verbose_name="usuário")
    exam = models.ForeignKey("admissions.EntranceExam", on_delete=models.CASCADE, related_name="favorited_by", verbose_name="processo seletivo")
    created_at = models.DateTimeField("salvo em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "exam"], name="unique_user_favorite_exam")]
        verbose_name = "vestibular salvo"
        verbose_name_plural = "vestibulares salvos"

    def __str__(self):
        return f"{self.user} — {self.exam}"


class SavedMaterial(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_materials", verbose_name="usuário")
    material = models.ForeignKey("studies.StudyMaterial", on_delete=models.CASCADE, related_name="saved_by", verbose_name="material")
    created_at = models.DateTimeField("salvo em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "material"], name="unique_user_saved_material")]
        verbose_name = "material salvo"
        verbose_name_plural = "materiais salvos"

    def __str__(self):
        return f"{self.user} — {self.material}"


class FavoriteCalendarEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_calendar_events", verbose_name="usuário")
    event = models.ForeignKey("admissions.CalendarEvent", on_delete=models.CASCADE, related_name="favorited_by", verbose_name="evento")
    created_at = models.DateTimeField("salvo em", auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "event"], name="unique_user_favorite_event")]
        verbose_name = "evento salvo"
        verbose_name_plural = "eventos salvos"

    def __str__(self):
        return f"{self.user} — {self.event}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications", verbose_name="usuário")
    title = models.CharField("título", max_length=180)
    message = models.TextField("mensagem")
    exam = models.ForeignKey("admissions.EntranceExam", on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications", verbose_name="processo seletivo")
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    read_at = models.DateTimeField("lido em", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "aviso interno"
        verbose_name_plural = "avisos internos"

    def __str__(self):
        return self.title

    @property
    def is_read(self):
        return self.read_at is not None
