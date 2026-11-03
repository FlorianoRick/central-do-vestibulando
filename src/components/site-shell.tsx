import Link from "next/link";
import { navItems } from "@/data/site-data";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3" aria-label="Central do Vestibulando home">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-700 to-violet-600 text-lg font-black text-white shadow-lg shadow-blue-200">
            C
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-700">Central</p>
            <p className="text-lg font-bold text-slate-900">do Vestibulando</p>
          </div>
        </Link>

        <nav className="hidden gap-5 text-sm font-medium text-slate-600 lg:flex">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="transition hover:text-blue-700">
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <Link
            href="/vestibulares"
            className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:text-blue-700"
          >
            Explorar
          </Link>
          <Link
            href="/planejamento"
            className="rounded-full bg-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-200 transition hover:bg-blue-800"
          >
            Meu planejamento
          </Link>
        </div>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-slate-200 bg-slate-950 text-slate-200">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1.2fr_0.8fr_0.8fr] lg:px-8">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-300">Central do Vestibulando</p>
          <p className="mt-4 max-w-md text-sm text-slate-300">
            Plataforma centralizadora para acompanhar vestibulares, prazos, materiais e organização de estudos.
          </p>
        </div>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-100">Navegação</h3>
          <ul className="mt-4 space-y-2 text-sm text-slate-300">
            {navItems.slice(0, 5).map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="transition hover:text-white">
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-100">Aviso</h3>
          <p className="mt-4 text-sm text-slate-300">
            Esta primeira versão utiliza dados de demonstração para validar a experiência e o fluxo da plataforma.
          </p>
        </div>
      </div>
    </footer>
  );
}
