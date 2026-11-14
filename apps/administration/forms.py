from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("is_active", "is_staff", "is_superuser")

    def __init__(self, *args, actor, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:
            return cleaned_data

        current = get_user_model().objects.get(pk=self.instance.pk)
        remains_active_superuser = (
            cleaned_data.get("is_active") and cleaned_data.get("is_superuser")
        )
        removes_active_superuser = (
            current.is_active
            and current.is_superuser
            and not remains_active_superuser
        )
        if self.actor.pk == current.pk and not remains_active_superuser:
            raise ValidationError(
                "Não é possível remover as próprias permissões administrativas."
            )
        if removes_active_superuser and not get_user_model().objects.filter(
            is_active=True,
            is_superuser=True,
        ).exclude(pk=current.pk).exists():
            raise ValidationError(
                "Não é possível remover ou desativar a última pessoa administradora ativa."
            )
        return cleaned_data
