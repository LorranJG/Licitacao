import { NextRequest, NextResponse } from "next/server";

import { backendUrl, SESSION_COOKIE } from "@/lib/session";

type RouteContext = {
  params: Promise<{ action: string }>;
};

function clientIp(request: NextRequest): string {
  return (request.headers.get("x-forwarded-for") || "")
    .split(",")[0]
    .trim();
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { action } = await context.params;
  if (action === "logout") {
    const response = NextResponse.json({ ok: true });
    response.cookies.delete(SESSION_COOKIE);
    return response;
  }
  const publicActions = [
    "login",
    "registrar",
    "solicitar-redefinicao",
    "redefinir-senha",
    "confirmar-email",
  ];
  if (!publicActions.includes(action)) {
    return NextResponse.json({ detail: "Ação inválida." }, { status: 404 });
  }

  const response = await fetch(`${backendUrl()}/auth/${action}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Real-IP": clientIp(request),
    },
    body: await request.text(),
    cache: "no-store",
  });
  const body = await response.json();
  if (!response.ok) {
    return NextResponse.json(body, { status: response.status });
  }

  if (action !== "login" && action !== "registrar") {
    return NextResponse.json(body, { status: response.status });
  }
  const nextResponse = NextResponse.json({ usuario: body.usuario });
  nextResponse.cookies.set(SESSION_COOKIE, body.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.SESSION_COOKIE_SECURE === "true",
    maxAge: body.expires_in,
    path: "/",
  });
  return nextResponse;
}
