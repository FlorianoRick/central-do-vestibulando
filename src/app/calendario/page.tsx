import { calendarEvents } from "@/data/site-data";

export default function CalendarioPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="mb-10">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-700">Calendário</p>
        <h1 className="mt-3 text-4xl font-black text-slate-900">Eventos e prazos em um só painel</h1>
        <p className="mt-3 max-w-3xl text-slate-600">
          Acompanhe abertura e encerramento de inscrições, provas, divulgação de resultados e matrículas por instituição.
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900">Próximos eventos</h2>
            <span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700">Dados de exemplo</span>
          </div>

          <div className="space-y-4">
            {calendarEvents.map((event) => (
              <div key={`${event.title}-${event.date}`} className="flex items-start gap-4 rounded-2xl bg-slate-50 p-4">
                <div className="flex h-12 w-12 flex-col items-center justify-center rounded-xl bg-blue-100 text-center text-sm font-semibold text-blue-800">
                  <span>{new Date(event.date).toLocaleDateString("pt-BR", { day: "2-digit" })}</span>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-slate-900">{event.title}</p>
                  <p className="mt-1 text-sm text-slate-600">{event.institution}</p>
                </div>
                <span className="rounded-full bg-slate-200 px-2.5 py-1 text-xs font-medium capitalize text-slate-700">
                  {event.type}
                </span>
              </div>
            ))}
          </div>
        </div>

        <aside className="space-y-6 rounded-3xl border border-slate-200 bg-slate-50 p-6 shadow-sm">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Conflitos detectados</h3>
            <p className="mt-2 text-sm text-slate-600">A plataforma identifica quando duas provas ou eventos importantes ocorrem no mesmo dia.</p>
          </div>

          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm font-semibold text-amber-800">Exemplo de conflito</p>
            <p className="mt-2 text-sm text-amber-700">COMVEST e UFRGS possuem provas no mesmo período em um cenário de demonstração da funcionalidade.</p>
          </div>

          <div className="rounded-2xl bg-slate-900 p-4 text-slate-100">
            <p className="text-sm text-slate-300">Próximo evento em destaque</p>
            <p className="mt-2 text-2xl font-black">08:00</p>
            <p className="mt-1 text-sm text-slate-300">Até a próxima prova</p>
          </div>
        </aside>
      </section>
    </main>
  );
}
