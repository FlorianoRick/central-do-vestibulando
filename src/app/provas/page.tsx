import { examsArchive } from "@/data/site-data";

export default function ProvasPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="mb-10">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-700">Provas e gabaritos</p>
        <h1 className="mt-3 text-4xl font-black text-slate-900">Banco de provas anteriores</h1>
        <p className="mt-3 max-w-3xl text-slate-600">
          Gerencie acesso a provas, gabaritos, resoluções comentadas e materiais por instituição, ano e disciplina.
        </p>
      </section>

      <section id="gabarios" className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900">Documentos disponíveis</h2>
          <span className="rounded-full bg-blue-100 px-2.5 py-1 text-xs font-semibold text-blue-700">Fonte: oficial</span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-100 text-slate-800">
              <tr>
                <th className="px-4 py-3">Instituição</th>
                <th className="px-4 py-3">Ano</th>
                <th className="px-4 py-3">Curso</th>
                <th className="px-4 py-3">Tipo</th>
                <th className="px-4 py-3">Prova</th>
                <th className="px-4 py-3">Gabarito</th>
              </tr>
            </thead>
            <tbody>
              {examsArchive.map((item) => (
                <tr key={`${item.institution}-${item.year}-${item.title}`} className="border-b border-slate-200">
                  <td className="px-4 py-3 font-semibold text-slate-800">{item.institution}</td>
                  <td className="px-4 py-3">{item.year}</td>
                  <td className="px-4 py-3">{item.course}</td>
                  <td className="px-4 py-3">{item.type}</td>
                  <td className="px-4 py-3">
                    <a href={item.url} target="_blank" rel="noreferrer" className="font-medium text-blue-700 underline">
                      Baixar PDF
                    </a>
                  </td>
                  <td className="px-4 py-3">
                    <a href={item.gabarito} target="_blank" rel="noreferrer" className="font-medium text-emerald-700 underline">
                      Ver gabarito
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
