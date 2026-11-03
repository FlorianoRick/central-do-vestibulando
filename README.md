# Central do Vestibulando

## Visão geral
Esta aplicação é uma primeira versão funcional de uma plataforma centralizadora de vestibulares do Brasil. O objetivo é reunir informações sobre processos seletivos, prazos, provas anteriores, comparações e materiais de estudo em um portal moderno e organizado.

## Arquitetura atual
- Frontend: Next.js, React, TypeScript e Tailwind CSS
- Roteamento: App Router do Next.js
- Organização: páginas por seção e dados centralizados em `src/data/site-data.ts`
- Componentização: header, footer e blocos reutilizáveis para visão geral e navegação

Consulte também [docs/arquitetura.md](docs/arquitetura.md) para a visão completa do projeto e do planejamento de expansão.

## Como executar
```bash
npm install
npm run dev
```

Acesse http://localhost:3000.

## Funcionalidades implementadas
- Dashboard inicial com métricas e destaques
- Catálogo de vestibulares
- Página de detalhe por vestibular
- Calendário resumido de eventos
- Banco de provas anteriores e gabaritos
- Página de comparação de processos
- Planejamento de estudos
- Seção de notícias e instituição
- Navegação e estrutura preparada para expansão

## Observações importantes
- Os dados desta primeira versão são demonstrativos e devem ser validados em produção com fontes oficiais.
- A aplicação foi estruturada para receber facilmente novas instituições, vestibulares e conteúdos.
