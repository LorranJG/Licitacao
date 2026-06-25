"use client";

import { RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

type AutoRefreshProps = {
  intervalSeconds?: number;
};

export function AutoRefresh({ intervalSeconds = 300 }: AutoRefreshProps) {
  const router = useRouter();

  useEffect(() => {
    const timer = window.setInterval(() => {
      router.refresh();
    }, intervalSeconds * 1000);

    return () => window.clearInterval(timer);
  }, [intervalSeconds, router]);

  return (
    <p className="flex items-center gap-2 text-xs font-medium text-slate-400">
      <RefreshCw aria-hidden="true" size={13} />
      Atualização automática a cada {Math.round(intervalSeconds / 60)} min
    </p>
  );
}
