import "server-only";

import { cookies } from "next/headers";

import type {
  BuscaSalva,
  Favorito,
  Lembrete,
  Usuario,
} from "@/types/licitacao";

export const SESSION_COOKIE = "radar_session";

export function backendUrl(): string {
  return (
    process.env.API_INTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

export async function sessionToken(): Promise<string | null> {
  return (await cookies()).get(SESSION_COOKIE)?.value ?? null;
}

async function authenticatedFetch(path: string): Promise<Response | null> {
  const token = await sessionToken();
  if (!token) return null;
  return fetch(`${backendUrl()}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
    signal: AbortSignal.timeout(10000),
  });
}

export async function getCurrentUser(): Promise<Usuario | null> {
  try {
    const response = await authenticatedFetch("/auth/me");
    if (!response?.ok) return null;
    return (await response.json()) as Usuario;
  } catch {
    return null;
  }
}

export async function getAccountData(): Promise<{
  favoritos: Favorito[];
  lembretes: Lembrete[];
  buscas: BuscaSalva[];
}> {
  const token = await sessionToken();
  if (!token) return { favoritos: [], lembretes: [], buscas: [] };
  const headers = { Authorization: `Bearer ${token}` };
  const [favoritosResponse, lembretesResponse, buscasResponse] = await Promise.all([
    fetch(`${backendUrl()}/favoritos`, {
      headers,
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    }),
    fetch(`${backendUrl()}/lembretes`, {
      headers,
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    }),
    fetch(`${backendUrl()}/buscas-salvas`, {
      headers,
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    }),
  ]);
  return {
    favoritos: favoritosResponse.ok
      ? ((await favoritosResponse.json()) as Favorito[])
      : [],
    lembretes: lembretesResponse.ok
      ? ((await lembretesResponse.json()) as Lembrete[])
      : [],
    buscas: buscasResponse.ok
      ? ((await buscasResponse.json()) as BuscaSalva[])
      : [],
  };
}
