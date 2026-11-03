import { newsFeed } from "@/data/site-data";

export default function NoticiasPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="mb-10">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-700">Notícias e atualizações</p>
        <h1 className="mt-3 text-4xl font-black text-slate-900">Alertas e novidades do cenário vestibular</h1>
      </section>

      <section className="space-y-6">
        {newsFeed.map((item) => (
          <article key={`${item.title}-${item.publishedAt}`} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">{item.institution}</p>
                <h2 className="mt-2 text-2xl font-bold text-slate-900">{item.title}</h2>
              </div>
              <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">Mudança importante</span>
            </div>

            <p className="mt-4 text-slate-600">{item.summary}</p>

            <div className="mt-5 flex flex-wrap gap-4 text-sm text-slate-500">
              <span>Publicado em {item.publishedAt}</span>
              <span>•</span>
              <span>Última atualização {item.updatedAt}</span>
              <span>•</span>
              <span>{item.source}</span>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
