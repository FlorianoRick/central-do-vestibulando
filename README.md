# Vestibulando

Plataforma Django para organizar a preparação para vestibulares, consultar provas anteriores, acessar materiais de estudo e acompanhar notícias com fonte revisada.

## O que está implementado

- Catálogo pesquisável e comparador de processos seletivos das instituições FATEC, UNESP, UNICAMP, USP e PUC-SP.
- Acervo pesquisável de provas e gabaritos, com filtros por instituição, curso, ano, fase e tipo de documento.
- Recursos externos por matéria com fonte e data de verificação; materiais demonstrativos são identificados.
- Notícias com fonte, data e estado de revisão editorial.
- Cadastro, entrada com usuário ou e-mail, recuperação e alteração de senha, perfil, preferências e exclusão da conta.
- Favoritos de vestibulares, materiais salvos, avisos internos, planos de estudo, sessões editáveis e resultados de simulados.
- Sugestões de sessões para sete dias, com prioridade para matérias compartilhadas quando o programa foi verificado.
- Painel interno em `/gestao/` para administrar conteúdo e papéis; o Django Admin continua disponível em `/admin/`.
- Editor visual com prévia, rascunho e publicação separada, incluindo textos da página inicial.
- Configuração local com SQLite e produção com PostgreSQL, Gunicorn e WhiteNoise.

`seed_demo_data` mantém registros de demonstração visivelmente identificados, sem inventar prazos ou links de inscrição. `seed_vestibulando_content` adiciona os recursos de estudo e as notícias iniciais com fonte e data de revisão. Datas e arquivos do acervo só aparecem como oficiais quando a fonte e o estado de publicação estão registrados.

## Estrutura

```text
config/                    Configuração Django, URLs e servidores WSGI/ASGI
apps/core/                 Página inicial, páginas informativas e comandos
apps/accounts/             Perfil, autenticação, favoritos, preferências e avisos
apps/admissions/           Catálogo, processos seletivos e acervo de documentos
apps/studies/              Matérias, materiais, comparação e planejamento
apps/news/                 Notícias e comunicados
apps/appearance/           Personalização visual e histórico de alterações
apps/administration/       Painel interno e gestão segura de papéis
templates/                 Template base e componentes compartilhados
static/                    CSS e JavaScript próprios
docs/                      Auditoria técnica e documentação do projeto
```

## Dados e relacionamentos

- Uma instituição possui processos seletivos; cada processo pode relacionar cursos, matérias, documentos, eventos e provas.
- Documentos de acervo registram edição, fase, curso, tipo, fonte, revisão e situação de publicação. Uploads aceitam PDF validado por assinatura e tamanho.
- Uma conta usa o sistema de autenticação do Django e possui perfil e preferências individuais.
- Favoritos, materiais salvos, avisos e resultados de simulados pertencem ao usuário autenticado.
- Um plano pertence a um usuário, relaciona vestibulares e matérias, e contém sessões ajustáveis.
- Recursos externos e notícias precisam de fonte e revisão antes da publicação. Notícias pendentes não aparecem nas páginas públicas.

As migrações de cada aplicativo ficam em `apps/*/migrations/`. O banco local é criado em `db.sqlite3`; configure `DATABASE_URL` para PostgreSQL.

## Autenticação e administração

O cadastro usa `django.contrib.auth`, validadores de senha do Django e hash seguro. O login aceita nome de usuário ou e-mail. As páginas privadas filtram os dados pelo usuário autenticado. A recuperação de senha usa os formulários e tokens do Django; localmente o e-mail é escrito no console. Para enviar mensagens em produção, configure as variáveis SMTP indicadas em `.env.example`.

Crie uma conta administrativa com `python manage.py createsuperuser`, entre em `/gestao/` e use o painel Django Admin em `/admin/` para CRUD de conteúdo. A gestão de papéis é restrita a superusuários, registra alterações no log administrativo, impede a remoção da última pessoa administradora ativa e não permite alterar senhas. Os papéis de usuário não são editáveis pelo Django Admin.

### Editor visual

Abra `/admin/design/` com uma conta superusuária ou com uma conta de equipe que tenha a permissão `appearance.change_siteappearance`. Escolha **Salvar rascunho** para manter alterações sem publicá-las ou **Publicar alterações** para ativá-las. A restauração geral registra a alteração no histórico.

As configurações visuais, o logotipo e o ícone são persistidos no banco de dados. Outros documentos enviados usam `MEDIA_ROOT`; em produção, configure armazenamento persistente antes de publicar provas, gabaritos ou imagens.

#### Preparar uma conta administrativa

Localmente, use `python manage.py createsuperuser`. O comando `bootstrap_superuser` só cria uma conta quando as três variáveis `BOOTSTRAP_SUPERUSER_USERNAME`, `BOOTSTRAP_SUPERUSER_EMAIL` e `BOOTSTRAP_SUPERUSER_PASSWORD` estão configuradas; ele não altera contas existentes nem imprime a senha. Não coloque essas variáveis no repositório. A promoção de contas de produção deve ser feita por uma pessoa autorizada em `/gestao/usuarios/`; não foi feita nenhuma alteração remota nesta implementação.

## Executar localmente

Requer Python 3.12 ou mais recente.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_demo_data
python manage.py seed_vestibulando_content
python manage.py createsuperuser
python manage.py runserver
```

Abra `http://127.0.0.1:8000/`. O banco SQLite é usado quando `DATABASE_URL` está vazio. O arquivo `.env` é local e não deve ser enviado ao Git.

## Verificações

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Publicação no Render

O repositório já contém um Blueprint em `render.yaml`, um script de build em `build.sh` e um script de inicialização em `start.sh`.

### Passo a passo

O `render.yaml` e os scripts existentes configuram o serviço, aplicam migrações e carregam dados. A publicação não foi executada como parte desta tarefa.

1. Revise as variáveis de ambiente e os recursos e custos exibidos no Render.
2. Configure PostgreSQL, `SECRET_KEY`, hosts/origens CSRF e SMTP antes de aceitar usuários.
3. Configure armazenamento persistente compatível com `MEDIA_ROOT` antes de publicar arquivos.
4. Faça deploy somente após revisar a branch e autorizar a publicação.
5. Após o deploy, crie ou promova a conta administrativa por um procedimento autorizado e remova variáveis de bootstrap temporárias.

O Blueprint gera `SECRET_KEY`, define `DJANGO_DEBUG=false`, conecta `DATABASE_URL` ao PostgreSQL e define os hosts e origens CSRF para `.onrender.com`. Se usar domínio próprio, acrescente o domínio a `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` nas variáveis do serviço.

O armazenamento de arquivos carregados usa o armazenamento local padrão do Django. O disco do serviço não é persistente entre deploys sem armazenamento durável; configure um disco compatível ou armazenamento S3 antes de publicar documentos. Não há credenciais de armazenamento incluídas neste repositório.

O envio de recuperação de senha por e-mail também precisa de um serviço SMTP. Configure as variáveis `EMAIL_*` listadas em `.env.example`; sem isso, Django usa o backend de console e não entrega e-mails aos estudantes.

## Pacote de código

Execute `python manage.py export_source_bundle` para gerar `exports/vestibulando-source.zip` e `exports/source-reference.html`. O pacote exclui ambientes virtuais, banco local, mídia, caches e arquivos de segredo; não inclua esses itens manualmente ao compartilhar o projeto.
- E-mail externo depende de configuração SMTP; notificações por push, Google Calendar, APIs de instituições e coleta automatizada ainda não estão conectados.
- A fila administrativa permite revisar alterações manualmente. Não há scraping automático nem tentativa de contornar regras de sites.
- Editais, provas, gabaritos e prazos devem ser adicionados por um administrador com fonte verificável. O banco de demonstração contém apenas exemplos sinalizados.

## Referências

O wireframe anexado e o prompt original estão preservados em `docs/references/`.
