type StatusBadgeProps = {
  status: string | null;
};

const styles: Record<string, string> = {
  aberta: "border-emerald-200 bg-emerald-50 text-emerald-700",
  encerrada: "border-slate-200 bg-slate-100 text-slate-600",
  cancelada: "border-red-200 bg-red-50 text-red-700",
  suspensa: "border-amber-200 bg-amber-50 text-amber-700",
  divulgada: "border-blue-200 bg-blue-50 text-blue-700",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = status?.toLowerCase() ?? "não informado";
  const style = styles[normalized] ?? styles.divulgada;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-bold capitalize ${style}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {normalized}
    </span>
  );
}

