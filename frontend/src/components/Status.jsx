export function ErrorMessage({ children }) {
  if (!children) return null;
  return <p className="rounded-ui border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger" role="alert">{children}</p>;
}

export function EmptyState({ title, children }) {
  return (
    <section className="rounded-panel border border-dashed border-border bg-surface p-6 text-center">
      <h2 className="text-lg font-semibold">{title}</h2>
      {children && <p className="mt-2 text-sm text-muted">{children}</p>}
    </section>
  );
}

export function SkeletonCard() {
  return <div className="h-96 animate-pulse rounded-panel bg-elevated" aria-label="Loading" />;
}
