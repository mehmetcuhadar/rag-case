export async function extractDetail(res: Response): Promise<string> {
  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) {
    const j = await res.json().catch(() => null);
    return (j?.detail ?? "Request failed.").toString();
  }
  const t = await res.text().catch(() => "");
  return t || `Request failed (${res.status}).`;
}