"use client";

import { Clock3 } from "lucide-react";
import { useEffect, useState } from "react";

type DeadlineCountdownProps = {
  deadline: string | null;
  compact?: boolean;
  showLabel?: boolean;
};

function calculate(deadline: string): {
  label: string;
  urgent: boolean;
  closed: boolean;
} {
  const remaining = new Date(deadline).getTime() - Date.now();
  if (!Number.isFinite(remaining)) {
    return { label: "Prazo não informado", urgent: false, closed: false };
  }
  if (remaining <= 0) {
    return { label: "Prazo encerrado", urgent: true, closed: true };
  }

  const totalMinutes = Math.floor(remaining / 60000);
  const days = Math.floor(totalMinutes / 1440);
  const hours = Math.floor((totalMinutes % 1440) / 60);
  const minutes = totalMinutes % 60;
  const label =
    days > 0
      ? `${days}d ${hours}h restantes`
      : `${hours}h ${minutes}min restantes`;
  return { label, urgent: remaining <= 48 * 60 * 60 * 1000, closed: false };
}

export function DeadlineCountdown({
  deadline,
  compact = false,
  showLabel = true,
}: DeadlineCountdownProps) {
  const [state, setState] = useState<ReturnType<typeof calculate> | null>(null);

  useEffect(() => {
    if (!deadline) return;
    const update = () => setState(calculate(deadline));
    update();
    const timer = window.setInterval(update, 60000);
    return () => window.clearInterval(timer);
  }, [deadline]);

  if (!deadline) return null;
  const display = state ?? {
    label: "Calculando prazo...",
    urgent: false,
    closed: false,
  };

  return (
    <div
      className={[
        "flex items-center gap-2 rounded-xl font-semibold",
        compact ? "px-3 py-2 text-xs" : "px-4 py-3 text-sm",
        display.urgent
          ? "bg-amber-50 text-amber-800"
          : "bg-mint-50 text-mint-600",
      ].join(" ")}
      title={display.closed ? "O prazo informado já terminou" : undefined}
    >
      <Clock3 aria-hidden="true" size={compact ? 15 : 18} />
      <span>
        {showLabel ? "Prazo para proposta: " : ""}
        {display.label}
      </span>
    </div>
  );
}
