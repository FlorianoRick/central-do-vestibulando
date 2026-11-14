# Auditoria técnica inicial

## Escopo e segurança

Esta auditoria descreve o repositório e o banco SQLite local disponíveis antes da implementação. Nenhuma consulta à base de produção foi feita. Os registros desta máquina não são evidência da existência de uma conta ou de conteúdo na produção.

## Arquitetura encontrada

- Aplicação Django 5.2+, com templates Django, CSS e JavaScript próprios.
- Seis apps instalados: `core`, `accounts`, `admissions`, `studies`, `news` e `appearance`.
- Autenticação padrão Django, perfil separado, preferências, favoritos, avisos e planejador por usuário.
- SQLite local; configuração de produção por PostgreSQL via `DATABASE_URL`, Gunicorn e WhiteNoise em Render.
- Migrações existentes para todos os apps e carga idempotente de dados demonstrativos.
- Testes Django distribuídos entre contas, vestibulares, editor visual, estudos e páginas principais.

## Recursos já existentes

- Catálogo pesquisável e comparador de processos seletivos.
- Páginas de detalhes, filtros, calendário e exportação ICS.
- Modelos para instituições, vestibulares, eventos, editais/documentos e provas com arquivos ou links.
- Listagem de provas e gabaritos, materiais por matéria, notícias com fonte, cadastro/login e área da conta.
- Planejamento de estudos, sessões, resultados de simulados e edição de preferências.
- Django Admin para os modelos de conteúdo e editor visual administrativo já protegido por permissão.
- Editor de cores, tipografia e medidas, com prévia no navegador, persistência no banco e histórico de alterações.

## Estado e lacunas observadas

- As telas já possuem a estrutura geral das referências, mas o CSS e os valores padrão do editor são predominantemente claros, não correspondendo à paleta azul-marinho especificada.
- O template compartilhado ainda mostra a marca antiga e links para Calendário e Instituições; o início também contém esses atalhos.
- Há telas públicas individuais de calendário e instituições, mesmo que esses itens tenham sido explicitamente removidos do novo produto.
- A carga demonstrativa adiciona 14 instituições/processos, 13 matérias (incluindo Espanhol e Redação) e guias genéricos demonstrativos; não cria arquivos de provas. Ela não atende ao catálogo restrito, aos recursos por matéria nem às notícias iniciais solicitadas.
- `ExamPaper` concentra prova e gabarito em um único registro e não representa adequadamente edição/semestre, curso, tipos individuais de documento, status de publicação ou metadados de cada arquivo.
- `Institution` contém apenas o site principal, sem campos para vestibular, arquivo de provas ou última verificação da fonte.
- As notícias não têm categoria, publicação agendada, destaque ou fila de revisão editorial.
- O usuário administrador usa atualmente apenas o Django Admin e o editor visual; ainda não há painel de gestão próprio ou gestão interna de papéis.
- Não existe modelo de comentários. Não será criada uma área pública de comentários sem necessidade confirmada no produto.
- O editor atual salva e ativa as alterações no mesmo passo; não fornece rascunho/publicação separados nem textos editáveis da página inicial.
- A configuração Render não define armazenamento persistente para arquivos comuns; `MEDIA_ROOT` usa o sistema de arquivos local, que não é persistente por padrão no serviço.
- Não foi localizado mecanismo de exportação completa do código-fonte em ZIP nem documentação HTML do código.

## Banco local antes das alterações

O SQLite local estava com as migrações aplicadas e continha 1 usuário, 14 instituições ativas, 14 processos seletivos, nenhuma prova anterior, 13 matérias, 13 materiais e 3 notícias demonstrativas. Nenhum dado pessoal foi incluído nesta auditoria. Esses números são apenas um retrato local e não devem ser usados para inferir ou alterar dados de produção.

## Verificações de base

- `python manage.py check`: aprovado, sem problemas reportados.
- `python manage.py test`: 36 testes encontrados e aprovados.

## Plano de preservação e riscos

- Preservar os registros legados e as contas; restringir o catálogo público a cinco instituições por situação ativa/consulta, em vez de apagar instituições, cursos, processos ou relações.
- Usar migrações Django aditivas e comandos de carga idempotentes. Não apontar comandos locais para a base de produção.
- Verificar cada fonte antes de publicar datas, arquivos, notícias ou links oficiais. Se um documento não puder ser verificado ou hospedado, mostrar a fonte oficial e a indisponibilidade, sem fabricar arquivo.
- A conta de produção e o armazenamento externo exigem credenciais/acesso que não estão disponíveis nesta sessão. O processo administrativo será preparado e documentado, mas não será executado contra produção.
- A identidade pública e a navegação devem seguir as exclusões escritas do pedido, mesmo onde a referência antiga ainda mostra links de calendário ou instituições.
- Manter os assets visuais do editor em armazenamento persistido no banco, como atualmente; os outros arquivos precisam de armazenamento durável configurado para Render antes de uma publicação real.

## Repositório e referência de recuperação

- Branch local de implementação: `feature/vestibulando-major-overhaul`.
- Tag de referência: `backup/pre-vestibulando-overhaul`.
- Ambas apontavam para o mesmo commit-base antes das mudanças. Nenhuma publicação remota foi realizada.
