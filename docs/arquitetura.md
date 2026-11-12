# Arquitetura — Central do Vestibulando

## Objetivo

Reunir processos seletivos, prazos oficiais, provas anteriores, materiais de estudo e ferramentas de organização em uma aplicação web simples para estudantes brasileiros.

## Tecnologias

- Python e Django para lógica, formulários, autenticação, banco de dados e administração.
- Templates Django, HTML semântico, CSS próprio e JavaScript pequeno para interação responsiva.
- SQLite para desenvolvimento local e PostgreSQL por `DATABASE_URL` em produção.
- Gunicorn e WhiteNoise para publicação no Render.

## Aplicativos Django

- `apps.core`: página inicial, páginas institucionais e carregamento dos registros demonstrativos.
- `apps.accounts`: perfil, preferências, favoritos, materiais salvos e avisos internos.
- `apps.admissions`: instituições, cursos, processos seletivos, calendário, documentos, provas e histórico de alterações.
- `apps.studies`: matérias, materiais, planos, sessões, simulados e comparação de programas.
- `apps.news`: notícias e avisos com fonte e marcação de conteúdo demonstrativo.
- `apps.appearance`: aparência global, editor visual restrito à equipe e histórico de alterações.

## Relações centrais

Uma instituição possui vários processos seletivos. Cada processo pode relacionar cursos, matérias, documentos, prazos e provas. Um plano de estudos pertence a um usuário e relaciona vestibulares, matérias e sessões. Favoritos, preferências, avisos e resultados pertencem ao usuário autenticado.

O Django Admin é a ferramenta principal de gestão. Alterações em processos seletivos registram os campos modificados, o responsável e o horário. Um processo só pode receber situação confirmada quando não for demonstrativo e tiver uma fonte oficial cadastrada.

O editor visual fica em `/admin/design/`. Uma única linha `SiteAppearance` guarda opções validadas; um histórico registra as configurações anterior e nova e o usuário que publicou. O template base converte esses valores em variáveis CSS. Logotipo e ícone são armazenados por uma classe Django Storage no próprio banco, enquanto a prévia usa valores não salvos apenas no navegador. Somente o envio do formulário altera a aparência pública. Acesso exige superusuário ou equipe com a permissão `appearance.change_siteappearance`.

## Autenticação e privacidade

O projeto usa o usuário padrão do Django e seu sistema de hash de senhas. O perfil adicional armazena nome, cidade, estado e curso desejado. Consultas de informações pessoais são filtradas pelo usuário autenticado. A área da conta permite revisar dados, preferências e excluir a conta.

## Dados confiáveis

O comando `python manage.py seed_demo_data` inclui os 14 processos demonstrativos originais, além das matérias para estudo. Não cria datas, taxas, vagas, documentos ou links oficiais. A migração `0004_restore_demo_catalog` repõe esses cadastros demonstrativos em bancos que já haviam passado pela limpeza anterior; não altera registros existentes com os mesmos identificadores. A interface diferencia exemplos e informações pendentes. Só dados confirmados aparecem como oficiais e só eventos oficiais são exportados no calendário ICS.

Não há coleta automática de páginas. A fila de revisão administrativa permite avaliar possíveis alterações antes de atualizar um registro.

## Arquivos e publicação

Arquivos carregados usam o armazenamento do Django. O armazenamento local é apropriado para desenvolvimento; antes de publicar documentos em uma instância Render efêmera, configure armazenamento persistente compatível com S3. Credenciais são fornecidas por variáveis de ambiente e não ficam no repositório.

`render.yaml` define o serviço Django e PostgreSQL. `build.sh` instala dependências e coleta os arquivos estáticos. O comando de inicialização aplica migrações, carrega dados demonstrativos idempotentes e executa Gunicorn.

O editor aceita logotipos PNG, JPEG ou WebP de até 2 MB e ícones PNG ou ICO de até 512 KB. As imagens são verificadas por tipo, conteúdo e resolução antes de serem persistidas no banco. Os demais arquivos enviados ao site continuam em `MEDIA_ROOT`; em produção, aponte esse diretório para armazenamento persistente.
