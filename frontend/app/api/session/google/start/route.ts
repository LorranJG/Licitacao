import { randomBytes } from "node:crypto";

import { NextRequest, NextResponse } from "next/server";

const STATE_COOKIE = "google_oauth_state";
const NONCE_COOKIE = "google_oauth_nonce";

function secureCookie(): boolean {
  return process.env.SESSION_COOKIE_SECURE === "true";
}

export async function GET(request: NextRequest) {
  const publicUrl = request.nextUrl.origin;
  const clientId = process.env.GOOGLE_CLIENT_ID;
  if (!clientId) {
    return NextResponse.redirect(
      new URL("/login?erro=google_nao_configurado", publicUrl),
    );
  }

  const state = randomBytes(32).toString("base64url");
  const nonce = randomBytes(32).toString("base64url");
  const redirectUri = new URL("/api/session/google/callback", publicUrl);
  const authorizationUrl = new URL(
    "https://accounts.google.com/o/oauth2/v2/auth",
  );
  authorizationUrl.search = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri.toString(),
    response_type: "code",
    scope: "openid email profile",
    state,
    nonce,
    prompt: "select_account",
  }).toString();

  const response = NextResponse.redirect(authorizationUrl);
  const cookieOptions = {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: secureCookie(),
    maxAge: 600,
    path: "/",
  };
  response.cookies.set(STATE_COOKIE, state, cookieOptions);
  response.cookies.set(NONCE_COOKIE, nonce, cookieOptions);
  return response;
}
