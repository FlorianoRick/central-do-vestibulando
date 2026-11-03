import { examCatalog } from "@/data/site-data";

export default function InstituicoesPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="mb-10">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-700">Instituições</p>
        <h1 className="mt-3 text-4xl font-black text-slate-900">Portal de universidades e centros de ensino</h1>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {examCatalog.map((institution) => (
          <article key={institution.slug} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">{institution.category}</p>
            <h2 className="mt-3 text-2xl font-bold text-slate-900">{institution.institution}</h2>
            <p className="mt-2 text-sm text-slate-600">{institution.state} · {institution.city}</p>
            <div className="mt-5 flex flex-wrap gap-2">
              {institution.courses.slice(0, 3).map((course) => (
                <span key={`${institution.slug}-${course}`} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                  {course}
                </span>
              ))}
            </div>
            <a href={institution.officialUrl} target="_blank" rel="noreferrer" className="mt-6 inline-flex text-sm font-semibold text-blue-700 hover:underline">
              Acessar site oficial →
            </a>
          </article>
        ))}
      </section>
    </main>
  );
}
