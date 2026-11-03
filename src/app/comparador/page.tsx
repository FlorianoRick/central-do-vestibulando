import { examCatalog } from "@/data/site-data";

const selected = examCatalog.slice(0, 3);

export default function ComparadorPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <section className="mb-10">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-700">Comparador</p>
        <h1 className="mt-3 text-4xl font-black text-slate-900">Compare até três processos simultaneamente</h1>
        <p className="mt-3 max-w-3xl text-slate-600">
          Avalie cursos, taxas, datas e formatos para escolher os vestibulares que melhor se encaixam ao seu planejamento.
        </p>
      </section>

      <section className="overflow-x-auto rounded-3xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-left text-sm text-slate-700">
          <thead className="bg-slate-100 text-slate-800">
            <tr>
              <th className="px-4 py-3">Critério</th>
              {selected.map((exam) => (
                <th key={exam.slug} className="px-4 py-3">{exam.name}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-slate-200">
              <td className="px-4 py-3 font-semibold text-slate-900">Instituição</td>
              {selected.map((exam) => (
                <td key={`${exam.slug}-institution`} className="px-4 py-3">{exam.institution}</td>
              ))}
            </tr>
            <tr className="border-b border-slate-200">
              <td className="px-4 py-3 font-semibold text-slate-900">Cursos</td>
              {selected.map((exam) => (
                <td key={`${exam.slug}-courses`} className="px-4 py-3">{exam.courses.join(", ")}</td>
              ))}
            </tr>
            <tr className="border-b border-slate-200">
              <td className="px-4 py-3 font-semibold text-slate-900">Taxa</td>
              {selected.map((exam) => (
                <td key={`${exam.slug}-fee`} className="px-4 py-3">{exam.fee}</td>
              ))}
            </tr>
            <tr className="border-b border-slate-200">
              <td className="px-4 py-3 font-semibold text-slate-900">Próximo evento</td>
              {selected.map((exam) => (
                <td key={`${exam.slug}-date`} className="px-4 py-3">{exam.nextMilestone}</td>
              ))}
            </tr>
            <tr>
              <td className="px-4 py-3 font-semibold text-slate-900">Modalidade</td>
              {selected.map((exam) => (
                <td key={`${exam.slug}-modality`} className="px-4 py-3">{exam.modality}</td>
              ))}
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  );
}
