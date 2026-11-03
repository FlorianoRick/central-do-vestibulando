import Link from "next/link";
import { calendarEvents, examCatalog, newsFeed, studyMaterials, summaryStats } from "@/data/site-data";

export default function Home() {
  return (
    <main className="mx-auto max-w-7xl px-4 pb-16 pt-10 sm:px-6 lg:px-8">
      <section className="rounded-[2rem] bg-gradient-to-br from-slate-950 via-blue-950 to-violet-950 p-8 text-white shadow-2xl shadow-blue-200/30 sm:p-10 lg:p-12">
        <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-blue-200">Portal educacional</p>
            <h1 className="mt-5 text-4xl font-black leading-tight sm:text-5xl">
              Centralize inscrições, provas e planejamento de estudo em um único lugar.
            </h1>
            <p className="mt-5 max-w-xl text-base text-slate-200">
              A plataforma reúne vestibulares, eventos, prazos, materiais e organização para que o estudante acompanhe tudo com mais velocidade e menos esforço.
            </p>

            <form action="/vestibulares" method="get" className="mt-8 flex flex-col gap-3 sm:flex-row">
              <input
                name="q"
                placeholder="Buscar por instituição, curso ou vestibular"
                className="w-full rounded-full border border-white/10 bg-white/10 px-4 py-3 text-sm text-white placeholder:text-slate-300 focus:border-blue-300 focus:outline-none"
              />
              <button
                type="submit"
                className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-blue-900 transition hover:bg-slate-100"
              >
                Pesquisar
              </button>
            </form>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/vestibulares" className="rounded-full bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-500">
                Explorar vestibulares
              </Link>
              <Link href="/comparador" className="rounded-full border border-white/20 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/5">
                Comparar processos
              </Link>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-blue-200">Resumo</p>
            <div className="mt-5 space-y-4">
              {summaryStats.map((item) => (
                <div key={item.label} className="rounded-2xl border border-white/10 bg-slate-900/30 p-4">
                  <p className="text-3xl font-black text-white">{item.value}</p>
                  <p className="mt-1 text-sm text-slate-300">{item.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="mt-12 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {summaryStats.map((stat) => (
          <div key={stat.label} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">{stat.label}</p>
            <p className="mt-3 text-3xl font-black text-slate-900">{stat.value}</p>
          </div>
        ))}
      </section>

      <section className="mt-16">
        <div className="mb-6 flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-700">Destaques</p>
            <h2 className="mt-2 text-3xl font-black text-slate-900">Vestibulares em destaque</h2>
          </div>
          <Link href="/vestibulares" className="text-sm font-semibold text-blue-700 hover:underline">Ver todos</Link>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          {examCatalog.slice(0, 3).map((exam) => (
            <article key={exam.slug} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">{exam.category}</p>
                  <h3 className="mt-2 text-2xl font-black text-slate-900">{exam.name}</h3>
                </div>
                <span className="rounded-full bg-emerald-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.15em] text-emerald-700">
                  {exam.status}
                </span>
              </div>
              <p className="mt-4 text-sm text-slate-600">{exam.institution}</p>
              <p className="mt-3 text-sm text-slate-500">{exam.nextMilestone}</p>
              <Link href={`/vestibulares/${exam.slug}`} className="mt-5 inline-flex text-sm font-semibold text-blue-700 hover:underline">
                Ver detalhes →
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="mt-16 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center justify-between gap-3">
            <h2 className="text-2xl font-black text-slate-900">Calendário resumido</h2>
            <Link href="/calendario" className="text-sm font-semibold text-blue-700 hover:underline">Abrir calendário</Link>
          </div>
          <div className="space-y-4">
            {calendarEvents.map((event) => (
              <div key={`${event.title}-${event.date}`} className="flex items-center justify-between gap-4 rounded-2xl bg-slate-50 p-4">
                <div>
                  <p className="font-semibold text-slate-900">{event.title}</p>
                  <p className="mt-1 text-sm text-slate-500">{event.institution}</p>
                </div>
                <span className="text-sm font-medium text-slate-700">{new Date(event.date).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 shadow-sm">
          <h2 className="text-2xl font-black text-slate-900">Materiais em destaque</h2>
          <ul className="mt-5 space-y-3">
            {studyMaterials.map((material) => (
              <li key={material.title} className="rounded-2xl bg-white px-4 py-3 text-sm text-slate-700 shadow-sm">
                <span className="block font-semibold text-slate-900">{material.title}</span>
                <span>{material.subject} · {material.type}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="mt-16 grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-700">Atualizações</p>
          <h2 className="mt-3 text-2xl font-black text-slate-900">Notícias e avisos</h2>
          <div className="mt-5 space-y-4">
            {newsFeed.map((item) => (
              <article key={`${item.title}-${item.publishedAt}`} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">{item.institution}</p>
                <h3 className="mt-2 font-bold text-slate-900">{item.title}</h3>
                <p className="mt-2 text-sm text-slate-600">{item.summary}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-900 p-6 text-white shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-200">Checklist</p>
          <h2 className="mt-3 text-2xl font-black">Estrutura pronta para expansão</h2>
          <ul className="mt-5 space-y-3 text-sm text-slate-200">
            <li>• Catálogo de instituições e vestibulares</li>
            <li>• Página de detalhe por processo</li>
            <li>• Calendário e eventos importantes</li>
            <li>• Banco de provas anteriores e gabaritos</li>
            <li>• Planejamento de estudos e materiais</li>
            <li>• Comparador de vestibulares</li>
          </ul>
          <Link href="/planejamento" className="mt-6 inline-flex rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-100">
            Acessar planejamento
          </Link>
        </div>
      </section>
    </main>
  );
}
