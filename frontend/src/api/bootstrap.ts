import { refreshTokensOnce } from "./http";
import { useSession } from "../store/session";

export async function bootstrapAuth(): Promise<void> {
  const { refreshToken, logoutLocal } = useSession.getState();
  if (!refreshToken) return;

  const ok = await refreshTokensOnce();
  if (!ok) {
    // refresh token invalid/expired → clear local auth
    logoutLocal();
    // optional hard wipe:
    localStorage.removeItem("llmchat_session_v1");
  }
}