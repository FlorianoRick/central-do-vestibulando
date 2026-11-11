from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import UserPreferences, UserProfile

User = get_user_model()


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(label="Nome completo", max_length=160)
    email = forms.EmailField(label="E-mail")
    city = forms.CharField(label="Cidade", max_length=100, required=False)
    state = forms.ChoiceField(label="Estado", choices=[("", "Selecione") , *UserProfile._meta.get_field("state").choices], required=False)
    target_course = forms.CharField(label="Curso desejado", max_length=120, required=False)

    class Meta:
        model = User
        fields = ("full_name", "username", "email", "city", "state", "target_course")
        labels = {"username": "Nome de usuário"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Senha"
        self.fields["password2"].label = "Confirme a senha"
        self.fields["password1"].help_text = "Use pelo menos 8 caracteres e evite senhas comuns."

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["full_name"].strip().split(" ")[0]
        if commit:
            user.save()
            profile = user.profile
            profile.full_name = self.cleaned_data["full_name"].strip()
            profile.city = self.cleaned_data.get("city", "").strip()
            profile.state = self.cleaned_data.get("state", "")
            profile.target_course = self.cleaned_data.get("target_course", "").strip()
            profile.save()
        return user


class EmailLoginForm(AuthenticationForm):
    remember = forms.BooleanField(label="Lembrar desta sessão", required=False)
    username = forms.CharField(label="Usuário ou e-mail", widget=forms.TextInput(attrs={"autocomplete": "username"}))
    password = forms.CharField(label="Senha", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    def clean(self):
        username = self.cleaned_data.get("username", "")
        if "@" in username:
            user = User.objects.filter(email__iexact=username).only("username").first()
            if user:
                self.cleaned_data["username"] = user.get_username()
        return super().clean()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("full_name", "city", "state", "target_course")
        widgets = {"full_name": forms.TextInput(), "city": forms.TextInput()}


class EmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email",)
        labels = {"email": "E-mail"}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Já existe outra conta com este e-mail.")
        return email


class PreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ("study_reminders", "deadline_reminders", "email_notifications")
        labels = {
            "study_reminders": "Mostrar lembretes de estudo na minha conta",
            "deadline_reminders": "Mostrar lembretes de prazos na minha conta",
            "email_notifications": "Prefiro receber avisos por e-mail",
        }
