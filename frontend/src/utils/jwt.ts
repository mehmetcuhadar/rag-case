export function isJwtExpired(token: string, skewSeconds = 30): boolean {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return true;

    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = JSON.parse(atob(payload));

    const exp: number | undefined = json?.exp;
    if (!exp) return true;

    const now = Math.floor(Date.now() / 1000);
    return exp <= now + skewSeconds;
  } catch {
    return true;
  }
}