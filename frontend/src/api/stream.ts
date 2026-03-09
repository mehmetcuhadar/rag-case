import { useSession } from "../store/session";
import { refreshTokensOnce } from "./http";
import { extractDetail } from "./errors";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:5000";

export type StreamItem =
  | { kind: "data"; value: string }
  | { kind: "event"; value: string };

function parseSseLines(buffer: string): { items: StreamItem[]; rest: string } {
  const lines = buffer.split(/\r?\n/);
  const rest = lines.pop() ?? "";
  const items: StreamItem[] = [];

  for (const line of lines) {
    if (!line) continue;
    if (line.startsWith("event: ")) items.push({ kind: "event", value: line.slice(7) });
    else if (line.startsWith("data: ")) items.push({ kind: "data", value: line.slice(6) });
  }
  return { items, rest };
}

async function doStreamFetch(chatId: string, content: string, signal?: AbortSignal) {
  const { accessToken } = useSession.getState();

  return fetch(`${API_BASE}/v1/chats/${chatId}/messages:stream`, {
    method: "POST",
    signal,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    body: JSON.stringify({ content }),
  });
}

function expireSessionAndThrow(): never {
  const { logoutLocal } = useSession.getState();
  logoutLocal();
  localStorage.removeItem("llmchat_session_v1"); // optional but recommended with localStorage
  throw new Error("Session expired. Please log in again.");
}

export async function streamMessage(
  chatId: string,
  content: string,
  onItem: (it: StreamItem) => void,
  signal?: AbortSignal
): Promise<void> {
  let res: Response;

  try {
    res = await doStreamFetch(chatId, content, signal);
  } catch {
    throw new Error("Backend unreachable (network error).");
  }

  // 401 → refresh → retry once; if refresh fails, logout
  if (res.status === 401) {
    const ok = await refreshTokensOnce();
    if (!ok) {
      expireSessionAndThrow();
    }

    try {
      res = await doStreamFetch(chatId, content, signal);
    } catch {
      throw new Error("Backend unreachable (network error).");
    }

    if (res.status === 401) {
      // access still invalid even after refresh: treat as expired session
      expireSessionAndThrow();
    }
  }

  if (!res.ok || !res.body) {
    const detail = await extractDetail(res);
    // If backend says invalid token / expired etc, treat as session expired
    if (res.status === 401) expireSessionAndThrow();
    throw new Error(detail);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buf = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buf += decoder.decode(value, { stream: true });
    const { items, rest } = parseSseLines(buf);
    buf = rest;

    for (const it of items) {
      onItem(it);
      if (it.kind === "event" && (it.value === "done" || it.value === "error")) return;
    }
  }
}

async function doSendFetch(chatId: string, content: string, signal?: AbortSignal) {
  const { accessToken } = useSession.getState();

  return fetch(`${API_BASE}/v1/chats/${chatId}/messages`, {
    method: "POST",
    signal,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    body: JSON.stringify({ content }),
  });
}

export async function sendMessage(chatId: string, content: string, signal?: AbortSignal) {
  let res: Response;

  try {
    res = await doSendFetch(chatId, content, signal);
  } catch {
    throw new Error("Backend unreachable (network error).");
  }

  if (res.status === 401) {
    const ok = await refreshTokensOnce();
    if (!ok) expireSessionAndThrow();

    try {
      res = await doSendFetch(chatId, content, signal);
    } catch {
      throw new Error("Backend unreachable (network error).");
    }

    if (res.status === 401) expireSessionAndThrow();
  }

  if (!res.ok) {
    const detail = await extractDetail(res);
    if (res.status === 401) expireSessionAndThrow();
    throw new Error(detail);
  }

  return res.json();
}