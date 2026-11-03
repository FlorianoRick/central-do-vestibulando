import Link from "next/link";
import { notFound } from "next/navigation";
import { examCatalog } from "@/data/site-data";

export function generateStaticParams() {
  return examCatalog.map((exam) => ({ slug: exam.slug }));
}

export default async function VestibularDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const exam = examCatalog.find((item) => item.slug === slug);

  if (!exam) {
    notFound();
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <Link href="/vestibulares" className="inline-flex text-sm font-medium text-blue-700 hover:underline">
        ← Voltar ao catálogo
      </Link>

      <section className="mt-6 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-700">{exam.category}</p>
            <h1 className="mt-3 text-4xl font-black text-slate-900">{exam.name}</h1>
            <p className="mt-2 text-lg text-slate-600">{exam.institution}</p>
          </div>
          <span className="rounded-full bg-emerald-100 px-3 py-1.5 text-sm font-semibold text-emerald-700">{exam.status}</span>
        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl bg-slate-100 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Etapa</p>
            <p className="mt-2 text-lg font-bold text-slate-900">{exam.stage}</p>
          </div>
          <div className="rounded-2xl bg-slate-100 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Taxa</p>
            <p className="mt-2 text-lg font-bold text-slate-900">{exam.fee}</p>
          </div>
          <div className="rounded-2xl bg-slate-100 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Local</p>
            <p className="mt-2 text-lg font-bold text-slate-900">{exam.city}</p>
          </div>
          <div className="rounded-2xl bg-slate-100 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Fonte</p>
            <p className="mt-2 text-lg font-bold text-slate-900">{exam.sourceLabel}</p>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
          {exam.highlight}
        </div>

        <div className="mt-8 grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Descrição</h2>
            <p className="mt-3 text-slate-600">{exam.description}</p>

            <h2 className="mt-8 text-xl font-bold text-slate-900">Cursos e formatos</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {exam.courses.map((course) => (
                <span key={course} className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700">
                  {course}
                </span>
              ))}
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {exam.formats.map((format) => (
                <span key={format} className="rounded-full bg-blue-100 px-3 py-1.5 text-xs font-medium text-blue-700">
                  {format}
                </span>
              ))}
            </div>
          </div>

          <aside className="rounded-3xl bg-slate-900 p-6 text-slate-100">
            <h3 className="text-lg font-bold">Resumo do processo</h3>
            <ul className="mt-5 space-y-3 text-sm text-slate-300">
              <li>• Inscrição: {exam.fee}</li>
              <li>• Isenção disponível: {exam.isFeeExempt ? "Sim" : "Não"}</li>
              <li>• Estado: {exam.state}</li>
              <li>• Modalidade: {exam.modality}</li>
              <li>• Próxima etapa: {exam.nextMilestone}</li>
            </ul>
            <div className="mt-6 space-y-3">
              <a href={exam.officialUrl} target="_blank" rel="noreferrer" className="block rounded-full bg-white px-4 py-2 text-center text-sm font-semibold text-slate-900">
                Edital oficial
              </a>
              <a href={exam.sourceUrl} target="_blank" rel="noreferrer" className="block rounded-full border border-slate-600 px-4 py-2 text-center text-sm font-semibold text-white">
                Site da instituição
              </a>
            </div>
          </aside>
        </div>
      </section>
    </main>
  );
}
