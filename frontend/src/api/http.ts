import { useSession } from "../store/session";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:5000";

type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

export async function refreshTokensOnce(): Promise<boolean> {
  const { refreshToken, setTokens } = useSession.getState();
  if (!refreshToken) return false;

  const r = await fetch(`${API_BASE}/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!r.ok) return false;

  const data = await r.json();
  setTokens(data.access_token, data.refresh_token);
  return true;
}

export async function request<T>(
  method: HttpMethod,
  path: string,
  opts?: { json?: any; signal?: AbortSignal }
): Promise<{ ok: boolean; status: number; data?: T; raw: Response }> {
  const { accessToken } = useSession.getState();

  const doFetch = () =>
    fetch(`${API_BASE}${path}`, {
      method,
      signal: opts?.signal,
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: opts?.json ? JSON.stringify(opts.json) : undefined,
    });

  let res: Response;

  try {
    res = await doFetch();
  } catch (e: any) {
    // Browser-level network error (DNS, refused, proxy down, etc.)
    throw new Error("Backend unreachable (network error).");
  }

  if (res.status === 401) {
    const refreshed = await refreshTokensOnce();
    if (refreshed) {
      // retry once with new access token
      const { accessToken: newAccess } = useSession.getState();
      res = await fetch(`${API_BASE}${path}`, {
        method,
        signal: opts?.signal,
        headers: {
          "Content-Type": "application/json",
          ...(newAccess ? { Authorization: `Bearer ${newAccess}` } : {}),
        },
        body: opts?.json ? JSON.stringify(opts.json) : undefined,
      });
    }
  }

  const out: { ok: boolean; status: number; data?: T; raw: Response } = {
    ok: res.ok,
    status: res.status,
    raw: res,
  };

  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) {
    try {
      out.data = (await res.json()) as T;
    } catch {
      // ignore
    }
  }

  return out;
}