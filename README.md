# Central do Vestibulando

Plataforma Django em português para organizar processos seletivos, prazos oficiais, provas, materiais e planos de estudo.

## O que está implementado

- Catálogo pesquisável de vestibulares, instituições, cursos, estados e tipos de processo, com filtros e comparação lado a lado.
- Páginas de detalhe com inscrições, datas, documentos, prova, taxa, vagas, programa e situação de verificação.
- Calendário em lista, semana e mês, filtros por instituição e processos, aviso de conflito entre provas selecionadas e exportação ICS.
- Acervo pesquisável de provas anteriores e gabaritos, com indicação de fonte oficial.
- Materiais organizados por matéria e comparação de matérias cadastradas para até três vestibulares.
- Cadastro, entrada com usuário ou e-mail, recuperação e alteração de senha, perfil, preferências e exclusão da conta.
- Favoritos de vestibulares, materiais salvos, avisos internos, planos de estudo, sessões editáveis e resultados de simulados.
- Sugestões de sessões para sete dias, com prioridade para matérias compartilhadas quando o programa foi verificado.
- Painel Django Admin para conteúdo, fontes, documentos, revisões e histórico de alteração dos processos seletivos.
- Configuração local com SQLite e produção com PostgreSQL, Gunicorn e WhiteNoise.

O comando `seed_demo_data` cria cadastros demonstrativos somente para FATEC e UNESP, além de guias de estudo. Esses registros não contêm prazos ou links oficiais e aparecem marcados como demonstrativos. Cadastros só podem ser confirmados no painel com uma fonte oficial; datas não são inventadas.

## Estrutura

```text
config/                    Configuração Django, URLs e servidores WSGI/ASGI
apps/core/                 Página inicial, páginas informativas e comandos
apps/accounts/             Perfil, autenticação, favoritos, preferências e avisos
apps/admissions/           Instituições, processos, documentos, calendário e provas
apps/studies/              Matérias, materiais, comparação e planejamento
apps/news/                 Notícias e comunicados
templates/                 Template base e componentes compartilhados
static/                    CSS e JavaScript próprios
docs/references/           Prompt de projeto e wireframe usados como referência
```

## Dados e relacionamentos

- Uma instituição possui processos seletivos; cada processo pode relacionar cursos, matérias, documentos, eventos e provas.
- Provas anteriores podem relacionar uma matéria e guardar arquivo ou link da prova, gabarito e resolução.
- Uma conta usa o sistema de autenticação do Django e possui perfil e preferências individuais.
- Favoritos, materiais salvos, avisos e resultados de simulados pertencem ao usuário autenticado.
- Um plano pertence a um usuário, relaciona vestibulares e matérias, e contém sessões ajustáveis.
- Notícias e materiais aceitam fontes e marcação de conteúdo demonstrativo.

As migrações de cada aplicativo ficam em `apps/*/migrations/`. O banco local é criado em `db.sqlite3`; configure `DATABASE_URL` para PostgreSQL.

## Autenticação e administração

O cadastro usa `django.contrib.auth`, validadores de senha do Django e hash seguro. O login aceita nome de usuário ou e-mail. As páginas privadas filtram os dados pelo usuário autenticado. A recuperação de senha usa os formulários e tokens do Django; localmente o e-mail é escrito no console. Para enviar mensagens em produção, configure as variáveis SMTP indicadas em `.env.example`.

Crie uma conta administrativa com `python manage.py createsuperuser` e entre em `/admin/`. Somente usuários autorizados pelo Django podem administrar conteúdo. Ao confirmar um processo seletivo, o painel exige uma fonte oficial e registra quem verificou e quando.

## Executar localmente

Requer Python 3.12 ou mais recente.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
python manage.py runserver
```

Abra `http://127.0.0.1:8000/`. O banco SQLite é usado quando `DATABASE_URL` está vazio. O arquivo `.env` é local e não deve ser enviado ao Git.

## Verificações

```powershell
python manage.py check
python manage.py test
```

## Publicação no Render

O repositório já contém um Blueprint em `render.yaml`, um script de build em `build.sh` e um script de inicialização em `start.sh`.

### Passo a passo

1. Entre no [Render Dashboard](https://dashboard.render.com/) e escolha **New → Blueprint Instance**.
2. Conecte o GitHub, selecione `FlorianoRick/central-do-vestibulando` e a branch `master`.
3. Revise os recursos do Blueprint. Ele cria o serviço web e o PostgreSQL; confirme os planos e custos exibidos no Render.
4. Clique em **Apply**. O Render instala `requirements.txt`, coleta os arquivos estáticos, aplica as migrações, carrega dados demonstrativos e inicia o Gunicorn.
5. Acompanhe **Events** e **Logs** do serviço. Quando o deploy terminar, abra o endereço `.onrender.com` mostrado no Dashboard.
6. Para administrar conteúdo, abra o **Shell** do serviço e execute `python manage.py createsuperuser`. Acesse `/admin/` no domínio do site.
7. Cadastre processos e fontes oficiais para FATEC e UNESP. Os dois processos iniciais são demonstrativos, sem prazos ou links oficiais.

O Blueprint gera `SECRET_KEY`, define `DJANGO_DEBUG=false`, conecta `DATABASE_URL` ao PostgreSQL e define os hosts e origens CSRF para `.onrender.com`. Se usar domínio próprio, acrescente o domínio a `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` nas variáveis do serviço.

O armazenamento de arquivos carregados usa o armazenamento local padrão do Django. O disco do serviço não é persistente entre deploys sem um disco dedicado; configure um armazenamento compatível com S3 antes de publicar documentos importantes. Não há credenciais de armazenamento incluídas neste repositório.

O envio de recuperação de senha por e-mail também precisa de um serviço SMTP. Configure as variáveis `EMAIL_*` listadas em `.env.example`; sem isso, Django usa o backend de console e não entrega e-mails aos estudantes.

## Integrações e dados

- A exportação `.ics` está implementada e inclui apenas eventos oficiais confirmados.
- E-mail externo depende de configuração SMTP; notificações por push, Google Calendar, APIs de instituições e coleta automatizada ainda não estão conectados.
- A fila administrativa permite revisar alterações manualmente. Não há scraping automático nem tentativa de contornar regras de sites.
- Editais, provas, gabaritos e prazos devem ser adicionados por um administrador com fonte verificável. O banco de demonstração contém apenas exemplos sinalizados.

## Referências

O wireframe anexado e o prompt original estão preservados em `docs/references/`.
