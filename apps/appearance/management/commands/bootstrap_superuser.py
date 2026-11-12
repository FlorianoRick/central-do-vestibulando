import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction


ENVIRONMENT_VARIABLES = (
    "BOOTSTRAP_SUPERUSER_USERNAME",
    "BOOTSTRAP_SUPERUSER_EMAIL",
    "BOOTSTRAP_SUPERUSER_PASSWORD",
)


class Command(BaseCommand):
    help = "Cria o primeiro superusuário a partir de variáveis de ambiente, se necessário."

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("Já existe um superusuário; nenhuma conta foi alterada.")
            return

        values = {name: os.environ.get(name, "") for name in ENVIRONMENT_VARIABLES}
        if not any(values.values()):
            self.stdout.write("Bootstrap não configurado; nenhum superusuário foi criado.")
            return
        if not all(values.values()):
            missing = ", ".join(name for name, value in values.items() if not value)
            raise CommandError(f"Configure todas as variáveis de bootstrap. Faltando: {missing}.")

        username = values["BOOTSTRAP_SUPERUSER_USERNAME"].strip()
        email = values["BOOTSTRAP_SUPERUSER_EMAIL"].strip()
        password = values["BOOTSTRAP_SUPERUSER_PASSWORD"]
        if not username or not email or not password:
            raise CommandError("Usuário, e-mail e senha do superusuário são obrigatórios.")
        if User.USERNAME_FIELD != "username":
            raise CommandError("O bootstrap atual requer o campo de usuário padrão do Django.")
        try:
            validate_email(email)
        except ValidationError:
            raise CommandError("Informe um endereço de e-mail válido para o superusuário.") from None
        if len(username) > User._meta.get_field("username").max_length:
            raise CommandError("O nome de usuário é maior que o limite permitido.")
        if User.objects.filter(username__iexact=username).exists():
            raise CommandError("Esse nome de usuário já existe. Escolha outro para o superusuário inicial.")
        if User.objects.filter(email__iexact=email).exists():
            raise CommandError("Esse e-mail já pertence a uma conta. Escolha outro para o superusuário inicial.")

        candidate = User(username=username, email=email)
        try:
            validate_password(password, user=candidate)
        except ValidationError as error:
            raise CommandError("A senha não atende aos requisitos: " + " ".join(error.messages)) from None

        try:
            with transaction.atomic():
                if User.objects.filter(is_superuser=True).exists():
                    self.stdout.write("Já existe um superusuário; nenhuma conta foi alterada.")
                    return
                User._default_manager.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                )
        except IntegrityError:
            if User.objects.filter(is_superuser=True).exists():
                self.stdout.write("Já existe um superusuário; nenhuma conta foi alterada.")
                return
            raise CommandError("Não foi possível criar o superusuário. Verifique o usuário e o e-mail.") from None

        self.stdout.write(self.style.SUCCESS(f"Superusuário inicial {username!r} criado."))
