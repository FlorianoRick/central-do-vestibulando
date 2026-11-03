# Visão geral da arquitetura do Central do Vestibulando

## 1. Objetivo
A plataforma centraliza informações sobre vestibulares, editais, provas anteriores, gabaritos, calendário, materiais e organização de estudos em um ambiente web moderno, responsável e fácil de escalar.

## 2. Stack principal
- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS
- UI: componentes reutilizáveis e páginas com roteamento App Router
- Dados: modelo em TypeScript com fontes e status de confiabilidade
- Previsão de backend: PostgreSQL + Supabase para autenticação, armazenamento e dados persistentes
- Futuras integrações: e-mail, notificações push, ingestão automatizada de fontes oficiais

## 3. Estrutura de pastas
```text
src/
  app/
    calendario/
    comparador/
    instituicoes/
    noticias/
    planejamento/
    provas/
    vestibulares/
    globals.css
    layout.tsx
    page.tsx
  components/
    site-shell.tsx
  data/
    site-data.ts
  lib/
    (futuro: validações, utilitários, integrações)
public/
  (assets estáticos)
docs/
  arquitetura.md
```

## 4. Modelo de dados proposto
- Instituição
- Vestibular
- Curso
- EventDate
- Documento
- Prova
- Gabarito
- Disciplina
- Conteúdo programático
- Notícia
- Usuário
- Favorito
- Planejamento de estudo
- Progresso
- Notificação
- Fonte e histórico de atualização

### Campos importantes por registro
- nome
- instituição vinculada
- data de publicação
- status de confiabilidade
- URL da fonte oficial
- data verificada
- último update
- responsável pela alteração

## 5. Componentes principais
- Header e navegação global
- Dashboard inicial
- Catálogo de vestibulares
- Página de detalhe do vestibular
- Calendário e lista de eventos
- Banco de provas e gabaritos
- Painel de comparação
- Planejamento pessoal
- Seção de notícias e alertas

## 6. Estratégia de dados e confiabilidade
A plataforma separa claramente:
- dados públicos e referenciados
- fontes oficiais e links
- status de confirmação e revisão
- conteúdo demo/ilustrativo quando necessário para testes

A ideia é priorizar informações validadas em vez de exibir dados duvidosos ou estimados como oficiais.

## 7. Próximos passos recomendados
1. Integrar banco real com Supabase/PostgreSQL.
2. Implementar autenticação de usuários.
3. Criar painel administrativo com CRUD e histórico.
4. Conectar fontes oficiais e automatização de verificação.
5. Adicionar notificações e alertas por email.
6. Realizar testes E2E e deploy em produção.
