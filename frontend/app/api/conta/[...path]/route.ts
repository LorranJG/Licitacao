import { NextRequest, NextResponse } from "next/server";

import { backendUrl, sessionToken } from "@/lib/session";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

function clientIp(request: NextRequest): string {
  return (request.headers.get("x-forwarded-for") || "")
    .split(",")[0]
    .trim();
}

async function proxy(request: NextRequest, context: RouteContext) {
  const token = await sessionToken();
  if (!token) {
    return NextResponse.json(
      { detail: "Faça login para continuar." },
      { status: 401 },
    );
  }
  const { path } = await context.params;
  if (
    ![
      "auth",
      "favoritos",
      "lembretes",
      "telegram",
      "pagamentos",
      "buscas-salvas",
      "eventos",
    ].includes(path[0] || "")
  ) {
    return NextResponse.json({ detail: "Rota não permitida." }, { status: 404 });
  }
  const target = new URL(`${backendUrl()}/${path.join("/")}`);
  target.search = request.nextUrl.search;
  const body =
    request.method === "GET" || request.method === "HEAD"
      ? undefined
      : await request.text();
  const response = await fetch(target, {
    method: request.method,
    headers: {
      Authorization: `Bearer ${token}`,
      "X-Real-IP": clientIp(request),
      ...(body ? { "Content-Type": "application/json" } : {}),
    },
    body,
    cache: "no-store",
  });
  if (response.status === 204) {
    return new NextResponse(null, { status: 204 });
  }
  return new NextResponse(await response.text(), {
    status: response.status,
    headers: {
      "Content-Type":
        response.headers.get("Content-Type") || "application/json",
    },
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const DELETE = proxy;
