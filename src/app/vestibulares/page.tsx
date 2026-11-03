import Link from "next/link";
import { examCatalog } from "@/data/site-data";

export default function VestibularesPage() {
  return (
    <main id="materiais" className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="rounded-3xl bg-gradient-to-br from-slate-900 via-blue-900 to-violet-900 p-8 text-white shadow-2xl shadow-blue-200/40">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-200">Catálogo</p>
        <h1 className="mt-4 text-4xl font-black">Vestibulares em um só lugar</h1>
        <p className="mt-3 max-w-2xl text-base text-slate-200">
          Consulte processos seletivos, cursos, datas e condições de inscrição com filtros e comparação entre instituições.
        </p>
        <form action="/vestibulares" method="get" className="mt-8 flex flex-col gap-3 md:flex-row">
          <input
            name="q"
            placeholder="Buscar instituição, curso ou processo"
            className="w-full rounded-full border border-white/15 bg-white/10 px-4 py-3 text-sm text-white placeholder:text-slate-300 focus:border-blue-300 focus:outline-none"
          />
          <button
            type="submit"
            className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-blue-900 transition hover:bg-slate-100"
          >
            Pesquisar
          </button>
        </form>
      </section>

      <section className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {examCatalog.map((exam) => (
          <article key={exam.slug} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">{exam.category}</p>
                <h2 className="mt-2 text-2xl font-bold text-slate-900">{exam.name}</h2>
              </div>
              <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                {exam.status}
              </span>
            </div>

            <p className="mt-4 text-sm text-slate-600">{exam.institution}</p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
              <span>{exam.state}</span>
              <span>•</span>
              <span>{exam.city}</span>
              <span>•</span>
              <span>{exam.modality}</span>
            </div>

            <p className="mt-4 text-sm text-slate-600">{exam.description}</p>

            <div className="mt-5 flex flex-wrap gap-2">
              {exam.courses.map((course) => (
                <span key={course} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                  {course}
                </span>
              ))}
            </div>

            <dl className="mt-6 space-y-2 text-sm text-slate-600">
              <div className="flex justify-between gap-3">
                <dt>Próxima etapa</dt>
                <dd className="font-semibold text-slate-800">{exam.nextMilestone}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt>Taxa</dt>
                <dd className="font-semibold text-slate-800">{exam.fee}</dd>
              </div>
            </dl>

            <Link
              href={`/vestibulares/${exam.slug}`}
              className="mt-6 inline-flex rounded-full bg-blue-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-800"
            >
              Ver detalhes
            </Link>
          </article>
        ))}
      </section>
    </main>
  );
}
