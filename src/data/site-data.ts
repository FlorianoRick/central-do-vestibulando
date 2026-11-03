export type NavItem = {
  label: string;
  href: string;
};

export type ExamStatus = "Inscrições abertas" | "Próximas inscrições" | "Resultado" | "Em atualização";

export type Exam = {
  slug: string;
  name: string;
  institution: string;
  state: string;
  city: string;
  modality: string;
  category: string;
  status: ExamStatus;
  nextMilestone: string;
  formats: string[];
  courses: string[];
  description: string;
  sourceLabel: string;
  sourceUrl: string;
  stage: string;
  fee: string;
  isFeeExempt: boolean;
  officialUrl: string;
  highlight: string;
};

export const navItems: NavItem[] = [
  { label: "Início", href: "/" },
  { label: "Vestibulares", href: "/vestibulares" },
  { label: "Calendário", href: "/calendario" },
  { label: "Provas anteriores", href: "/provas" },
  { label: "Gabaritos", href: "/provas#gabarios" },
  { label: "Materiais", href: "/vestibulares#materiais" },
  { label: "Planejamento", href: "/planejamento" },
  { label: "Instituições", href: "/instituicoes" },
  { label: "Notícias", href: "/noticias" },
];

export const summaryStats = [
  { label: "Inscrições abertas", value: "12", tone: "emerald" },
  { label: "Próximas provas", value: "18", tone: "blue" },
  { label: "Resultados em breve", value: "4", tone: "amber" },
  { label: "Atualizações recentes", value: "9", tone: "rose" },
];

export const featuredExams: Exam[] = [
  {
    slug: "fuvest",
    name: "FUVEST",
    institution: "Universidade de São Paulo",
    state: "SP",
    city: "São Paulo",
    modality: "Vestibular",
    category: "Federal",
    status: "Inscrições abertas",
    nextMilestone: "Inscrições encerram em 14 dias",
    formats: ["1ª fase", "2ª fase"],
    courses: ["Medicina", "Direito", "Engenharia"],
    description: "Processo seletivo tradicional da USP com destaque para a etapa de redação e análise crítica.",
    sourceLabel: "Fuvest oficial",
    sourceUrl: "https://www.fuvest.br/",
    stage: "Processo seletivo 2027",
    fee: "R$ 157,00",
    isFeeExempt: true,
    officialUrl: "https://www.fuvest.br/",
    highlight: "Exemplo demonstrativo: as datas deste card representam uma simulação para apresentação da plataforma.",
  },
  {
    slug: "enem",
    name: "ENEM",
    institution: "INEP",
    state: "Brasil",
    city: "Nacional",
    modality: "Exame Nacional",
    category: "Nacional",
    status: "Próximas inscrições",
    nextMilestone: "Prova em 8 semanas",
    formats: ["Linguagens", "Ciências Humanas", "Natureza", "Matemática", "Redação"],
    courses: ["Sisu", "Prouni", "Fies"],
    description: "Sistema nacional de avaliação com grande impacto para acesso ao ensino superior e bolsas.",
    sourceLabel: "INEP",
    sourceUrl: "https://www.gov.br/inep/pt-br",
    stage: "Inscrições e aplicação",
    fee: "Gratuito",
    isFeeExempt: true,
    officialUrl: "https://enem.inep.gov.br/",
    highlight: "Dados marcados como exemplo para fins de arquitetura e prototipagem funcional.",
  },
  {
    slug: "unicamp",
    name: "COMVEST",
    institution: "Universidade Estadual de Campinas",
    state: "SP",
    city: "Campinas",
    modality: "Vestibular",
    category: "Estadual",
    status: "Resultado",
    nextMilestone: "Resultado previsto para 04/12",
    formats: ["Prova objetiva", "Redação"],
    courses: ["Computação", "Arquitetura", "Medicina"],
    description: "Vestibular da Unicamp conhecido pela exigência de raciocínio rápido e conteúdo rigoroso.",
    sourceLabel: "Unicamp oficial",
    sourceUrl: "https://www.unicamp.br/unicamp/",
    stage: "Resultado final",
    fee: "R$ 120,00",
    isFeeExempt: false,
    officialUrl: "https://www.unicamp.br/unicamp/vestibular",
    highlight: "Exemplo demonstrativo: datas e montantes ilustrativos para organização da interface.",
  },
];

export const examCatalog: Exam[] = [
  ...featuredExams,
  {
    slug: "unesp",
    name: "VUNESP",
    institution: "Universidade Estadual Paulista",
    state: "SP",
    city: "São Paulo",
    modality: "Vestibular",
    category: "Estadual",
    status: "Próximas inscrições",
    nextMilestone: "Inscrições abrem em 3 semanas",
    formats: ["Objetiva", "Dissertativa"],
    courses: ["Direito", "Arquitetura", "Odontologia"],
    description: "Vestibular estadual com foco em provas de alto nível e ampla presença em cursos de saúde e humanas.",
    sourceLabel: "Vunesp oficial",
    sourceUrl: "https://www.vunesp.com.br/",
    stage: "Processo seletivo 2027",
    fee: "R$ 86,00",
    isFeeExempt: true,
    officialUrl: "https://www.vunesp.com.br/",
    highlight: "Estrutura preparada para incluir editais, materiais e cronograma por instituição.",
  },
  {
    slug: "ufrgs",
    name: "UFRGS",
    institution: "Universidade Federal do Rio Grande do Sul",
    state: "RS",
    city: "Porto Alegre",
    modality: "Vestibular",
    category: "Federal",
    status: "Inscrições abertas",
    nextMilestone: "Prova em 22 dias",
    formats: ["Objetiva", "Redação"],
    courses: ["Engenharia", "Medicina", "Jornalismo"],
    description: "Processo seletivo reconhecido por oferecer ampla variedade de cursos e boa organização do calendário.",
    sourceLabel: "UFRGS oficial",
    sourceUrl: "https://www.ufrgs.br/",
    stage: "Edital em revisão",
    fee: "R$ 115,00",
    isFeeExempt: true,
    officialUrl: "https://www.ufrgs.br/vestibular/",
    highlight: "Exemplo de integração para lista de cursos, vagas e cronograma de eventos no sistema.",
  },
  {
    slug: "ifsp",
    name: "IFSP",
    institution: "Instituto Federal de São Paulo",
    state: "SP",
    city: "São Paulo",
    modality: "Vestibular",
    category: "Federal",
    status: "Em atualização",
    nextMilestone: "Edital pendente",
    formats: ["Objetiva", "Técnico"],
    courses: ["Análise e Desenvolvimento", "Automação", "Eletrônica"],
    description: "Processo seletivo para ensino técnico, tecnológico e superior em instituições federais.",
    sourceLabel: "IFSP oficial",
    sourceUrl: "https://www.ifsp.edu.br/",
    stage: "Aguardando publicação",
    fee: "R$ 70,00",
    isFeeExempt: true,
    officialUrl: "https://www.ifsp.edu.br/vestibular",
    highlight: "A plataforma enfatiza o rastreio de fontes e status de confiabilidade para cada atualização.",
  },
];

export const calendarEvents = [
  { title: "Inscrições FUVEST", date: "2026-11-12", type: "inscricao", institution: "USP" },
  { title: "Prova COMVEST", date: "2026-11-17", type: "prova", institution: "Unicamp" },
  { title: "Resultado UFRGS", date: "2026-11-24", type: "resultado", institution: "UFRGS" },
  { title: "Prazo de isenção ENEM", date: "2026-11-29", type: "isencao", institution: "INEP" },
  { title: "Edital IFSP", date: "2026-12-03", type: "edital", institution: "IFSP" },
  { title: "Matrículas UNESP", date: "2026-12-10", type: "matricula", institution: "Unesp" },
];

export const examsArchive = [
  {
    year: "2025",
    institution: "FUVEST",
    title: "Prova de Matemática e suas tecnologias",
    type: "Objetiva",
    url: "https://www.fuvest.br/",
    gabarito: "https://www.fuvest.br/",
    course: "Engenharia",
  },
  {
    year: "2024",
    institution: "UNESP",
    title: "Prova de Ciências Humanas",
    type: "Redação e objetiva",
    url: "https://www.vunesp.com.br/",
    gabarito: "https://www.vunesp.com.br/",
    course: "Direito",
  },
  {
    year: "2025",
    institution: "ENEM",
    title: "Redação e Linguagens",
    type: "Nacional",
    url: "https://enem.inep.gov.br/",
    gabarito: "https://enem.inep.gov.br/",
    course: "Nacional",
  },
];

export const newsFeed = [
  {
    title: "Edital complementar de vagas em instituições públicas",
    summary: "Atualização de cronograma com ajustes nas etapas de inscrição e seleção para cursos de destaque.",
    institution: "INEP",
    publishedAt: "2026-10-28",
    updatedAt: "2026-10-29",
    source: "Portal oficial",
  },
  {
    title: "Calendário do vestibular revisado pela instituição",
    summary: "Mudança de data para divulgação do resultado e matrículas foi publicada no portal oficial.",
    institution: "UFRGS",
    publishedAt: "2026-11-01",
    updatedAt: "2026-11-02",
    source: "Comissão organizadora",
  },
  {
    title: "Prazo de isenção ampliado",
    summary: "O gabinete de apoio ao estudante informou novo período para solicitação de redução de taxa.",
    institution: "FUVEST",
    publishedAt: "2026-11-03",
    updatedAt: "2026-11-03",
    source: "Comunicado oficial",
  },
];

export const studyMaterials = [
  { title: "Matemática para vestibular", subject: "Matemática", type: "Resumo e exercícios" },
  { title: "Física em foco", subject: "Física", type: "Teoria e listas" },
  { title: "Redação com estrutura clara", subject: "Redação", type: "Dicas e modelos" },
  { title: "Geografia e atualidades", subject: "Geografia", type: "Mapas mentais" },
];

export const plannerGoals = [
  { label: "Horas semanais", value: "14h" },
  { label: "Disciplinas em foco", value: "6" },
  { label: "Metas concluídas", value: "84%" },
  { label: "Próximas revisões", value: "3" },
];
