export function Button({ children, variant = "primary", className = "", ...props }) {
  const styles = variant === "ghost"
    ? "text-text hover:bg-elevated"
    : variant === "danger"
      ? "bg-danger text-white hover:brightness-95"
      : "bg-primary text-white hover:brightness-95";
  return (
    <button
      className={`min-h-[var(--tap-min)] rounded-ui px-4 py-2 text-sm font-semibold transition duration-150 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 ${styles} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
