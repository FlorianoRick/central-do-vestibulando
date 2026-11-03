import { plannerGoals, studyMaterials } from "@/data/site-data";

export default function PlanejamentoPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="mb-10">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-700">Planejamento</p>
        <h1 className="mt-3 text-4xl font-black text-slate-900">Organize sua rotina de estudos com clareza</h1>
      </section>

      <section className="grid gap-5 md:grid-cols-4">
        {plannerGoals.map((item) => (
          <div key={item.label} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">{item.label}</p>
            <p className="mt-3 text-3xl font-black text-slate-900">{item.value}</p>
          </div>
        ))}
      </section>

      <section className="mt-10 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900">Cronograma sugerido</h2>
          <div className="mt-6 space-y-4">
            {[
              "Matemática e redação em blocos matinais",
              "Química e biologia após o almoço",
              "Revisão de tópicos de humanidades à noite",
              "Simulados e correção aos finais de semana",
            ].map((step, index) => (
              <div key={step} className="flex items-center gap-4 rounded-2xl bg-slate-50 p-4">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-700 text-sm font-bold text-white">
                  {index + 1}
                </span>
                <p className="text-sm font-medium text-slate-700">{step}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 shadow-sm">
          <h2 className="text-xl font-bold text-slate-900">Materiais em destaque</h2>
          <ul className="mt-5 space-y-3">
            {studyMaterials.map((item) => (
              <li key={item.title} className="rounded-2xl bg-white p-3 text-sm text-slate-700 shadow-sm">
                <span className="block font-semibold text-slate-900">{item.title}</span>
                <span className="text-slate-500">{item.subject} · {item.type}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
