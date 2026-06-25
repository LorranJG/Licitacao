import { NextRequest, NextResponse } from "next/server";

import { backendUrl, SESSION_COOKIE } from "@/lib/session";

const STATE_COOKIE = "google_oauth_state";
const NONCE_COOKIE = "google_oauth_nonce";

function errorRedirect(request: NextRequest, error: string) {
  const publicUrl = process.env.APP_PUBLIC_URL || request.nextUrl.origin;
  const response = NextResponse.redirect(
    new URL(`/login?erro=${encodeURIComponent(error)}`, publicUrl),
  );
  response.cookies.delete(STATE_COOKIE);
  response.cookies.delete(NONCE_COOKIE);
  return response;
}

export async function GET(request: NextRequest) {
  const publicUrl = process.env.APP_PUBLIC_URL || request.nextUrl.origin;
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state");
  const storedState = request.cookies.get(STATE_COOKIE)?.value;
  const nonce = request.cookies.get(NONCE_COOKIE)?.value;

  if (!clientId || !clientSecret) {
    return errorRedirect(request, "google_nao_configurado");
  }
  if (!code || !state || !storedState || state !== storedState || !nonce) {
    return errorRedirect(request, "google_estado_invalido");
  }

  const redirectUri = new URL("/api/session/google/callback", publicUrl);
  const tokenResponse = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri.toString(),
      grant_type: "authorization_code",
    }),
    cache: "no-store",
  });
  if (!tokenResponse.ok) {
    return errorRedirect(request, "google_token_falhou");
  }
  const googleTokens = (await tokenResponse.json()) as { id_token?: string };
  if (!googleTokens.id_token) {
    return errorRedirect(request, "google_token_ausente");
  }

  const radarResponse = await fetch(`${backendUrl()}/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_token: googleTokens.id_token, nonce }),
    cache: "no-store",
  });
  if (!radarResponse.ok) {
    return errorRedirect(request, "google_login_falhou");
  }
  const body = (await radarResponse.json()) as {
    access_token: string;
    expires_in: number;
  };

  const response = NextResponse.redirect(new URL("/conta", publicUrl));
  response.cookies.set(SESSION_COOKIE, body.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.SESSION_COOKIE_SECURE === "true",
    maxAge: body.expires_in,
    path: "/",
  });
  response.cookies.delete(STATE_COOKIE);
  response.cookies.delete(NONCE_COOKIE);
  return response;
}
