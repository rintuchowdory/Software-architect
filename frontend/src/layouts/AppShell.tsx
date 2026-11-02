import { NavLink, Outlet, Navigate, Link } from "react-router-dom";
import { CodeXml, LayoutDashboard, Users, FolderKanban, Wallet, LogOut, ClipboardList } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/cn";

const nav = [
  { to: "/app", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/app/clients", label: "Clients", icon: Users },
  { to: "/app/projects", label: "Projects", icon: FolderKanban },
  { to: "/app/financials", label: "Financials", icon: Wallet },
];

export default function AppShell() {
  const { user, logout } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="flex min-h-screen bg-ink-950">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-white/5 bg-ink-900/60 sm:flex print:hidden">
        <div className="flex items-center gap-2 px-6 py-6">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-signal-400 to-accent-500 text-ink-950">
            <CodeXml size={18} strokeWidth={2.5} />
          </span>
          <span className="font-display text-[15px] font-semibold text-slate-100">Software Architect</span>
        </div>

        <nav className="flex-1 space-y-1 px-3">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition",
                  isActive
                    ? "bg-signal-400/10 text-signal-400"
                    : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                )
              }
            >
              <item.icon size={17} />
              {item.label}
            </NavLink>
          ))}

          <div className="px-3 pt-4 pb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-600">
            Client-facing
          </div>
          <Link
            to="/intake"
            target="_blank"
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition hover:bg-white/5 hover:text-slate-200"
          >
            <ClipboardList size={17} />
            Intake form
          </Link>
        </nav>

        <div className="border-t border-white/5 p-3">
          <div className="flex items-center gap-3 rounded-lg px-3 py-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-ink-700 text-xs font-semibold text-slate-200">
              {user.name.slice(0, 2).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-200">{user.name}</p>
              <p className="truncate text-xs text-slate-500">{user.email}</p>
            </div>
            <button
              onClick={logout}
              title="Sign out"
              className="rounded-md p-1.5 text-slate-500 transition hover:bg-white/5 hover:text-slate-200"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Mobile: the sidebar is hidden below sm, so navigation lives here. */}
        <div className="flex items-center justify-between border-b border-white/5 px-4 py-3 sm:hidden print:hidden">
          <Link to="/app" className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-signal-400 to-accent-500 text-ink-950">
              <CodeXml size={14} strokeWidth={2.5} />
            </span>
            <span className="font-display text-sm font-semibold text-slate-100">Software Architect</span>
          </Link>
          <button onClick={logout} className="rounded-md p-1.5 text-slate-500">
            <LogOut size={16} />
          </button>
        </div>

        <nav className="flex gap-1 overflow-x-auto border-b border-white/5 px-3 py-2 sm:hidden print:hidden">
          {[...nav, { to: "/intake", label: "Intake", end: false }].map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-medium transition",
                  isActive ? "bg-signal-400/10 text-signal-400" : "text-slate-400"
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <main className="flex-1 px-4 py-6 sm:px-10 sm:py-8 print:p-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
