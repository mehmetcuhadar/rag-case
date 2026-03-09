import { request } from "./http";
import { useSession } from "../store/session";

type TokenResponse = { access_token: string; refresh_token: string };

export async function login(username: string, password: string) {
  const r = await request<TokenResponse>("POST", "/v1/auth/login", {
    json: { username, password },
  });
  if (!r.ok) throw await extractDetail(r.raw);

  const { setTokens, setUsername, setAuthError, setChatId } = useSession.getState();
  setAuthError(null);
  setTokens(r.data!.access_token, r.data!.refresh_token);
  setUsername(username);
  setChatId(null);
}

export async function register(username: string, password: string) {
  const r = await request<TokenResponse>("POST", "/v1/auth/register", {
    json: { username, password },
  });
  if (!r.ok) throw await extractDetail(r.raw);

  const { setTokens, setUsername, setAuthError, setChatId } = useSession.getState();
  setAuthError(null);
  setTokens(r.data!.access_token, r.data!.refresh_token);
  setUsername(username);
  setChatId(null);
}

export async function logout() {
  const { refreshToken, logoutLocal } = useSession.getState();
  if (refreshToken) {
    // best-effort revoke
    await request("POST", "/v1/auth/logout", { json: { refresh_token: refreshToken } });
  }
  logoutLocal();
}

async function extractDetail(res: Response): Promise<Error> {
  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) {
    const j = await res.json().catch(() => null);
    return new Error(j?.detail ?? "Request failed.");
  }
  return new Error("Request failed.");
}