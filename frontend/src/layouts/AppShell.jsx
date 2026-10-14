"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Search, SquarePlus, User, Shield } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/Button";

const nav = [
  { href: "/", label: "Feed", icon: Home },
  { href: "/search", label: "Search", icon: Search },
  { href: "/upload", label: "Post", icon: SquarePlus },
  { href: "/settings", label: "Profile", icon: User }
];

export function AppShell({ children }) {
  const pathname = usePathname();
  const { user, status, logout } = useAuth();
  const items = user?.role === "admin" ? [...nav, { href: "/admin", label: "Admin", icon: Shield }] : nav;
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[var(--sidebar-width)_1fr]">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-[var(--sidebar-width)] border-r border-border bg-surface px-5 py-6 lg:block">
        <Link href="/" className="block text-xl font-black tracking-normal">Peer Meet</Link>
        <nav className="mt-8 space-y-2" aria-label="Primary">
          {items.map((item) => <NavItem key={item.href} item={item} active={pathname === item.href} />)}
        </nav>
        <div className="absolute bottom-6 left-5 right-5">
          {status === "authenticated" ? (
            <div className="space-y-3">
              <p className="text-sm text-muted">@{user.username}</p>
              <Button variant="ghost" className="w-full border border-border" onClick={logout}>Log out</Button>
            </div>
          ) : <Link className="text-sm font-semibold text-primary" href="/login">Sign in</Link>}
        </div>
      </aside>
      <header className="sticky top-0 z-10 border-b border-border bg-surface/95 px-4 py-3 backdrop-blur lg:hidden">
        <div className="flex items-center justify-between">
          <Link href="/" className="font-black">Peer Meet</Link>
          {status === "authenticated" ? <span className="text-sm text-muted">@{user.username}</span> : <Link className="text-sm font-semibold text-primary" href="/login">Sign in</Link>}
        </div>
      </header>
      <main className="px-[var(--page-gutter)] pb-[calc(var(--mobile-nav-height)+1rem)] pt-5 lg:col-start-2 lg:pb-10 lg:pt-8">{children}</main>
      <nav className="fixed bottom-0 left-0 right-0 z-20 grid h-[var(--mobile-nav-height)] grid-cols-4 border-t border-border bg-surface/95 px-2 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden" aria-label="Primary">
        {nav.map((item) => <MobileItem key={item.href} item={item} active={pathname === item.href} />)}
      </nav>
    </div>
  );
}

function NavItem({ item, active }) {
  const Icon = item.icon;
  return (
    <Link href={item.href} className={`flex min-h-[var(--tap-min)] items-center gap-3 rounded-ui px-3 text-sm font-semibold transition ${active ? "bg-elevated text-primary" : "text-muted hover:bg-elevated hover:text-text"}`}>
      <Icon size={20} aria-hidden />
      {item.label}
    </Link>
  );
}

function MobileItem({ item, active }) {
  const Icon = item.icon;
  return (
    <Link href={item.href} className={`flex flex-col items-center justify-center gap-1 text-xs font-semibold ${active ? "text-primary" : "text-muted"}`}>
      <Icon size={21} aria-hidden />
      {item.label}
    </Link>
  );
}
