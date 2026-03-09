import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Role = "user" | "assistant";
export type UiMessage = { role: Role; content: string };

type SessionState = {
  username: string | null;
  accessToken: string | null;
  refreshToken: string | null;

  chatId: string | null;
  messagesByChat: Record<string, UiMessage[]>;

  renameChatId: string | null;
  deleteChatId: string | null;
  authError: string | null;

  setUsername: (u: string | null) => void;
  setTokens: (access: string | null, refresh: string | null) => void;

  setChatId: (chatId: string | null) => void;
  setMessagesForChat: (chatId: string, msgs: UiMessage[]) => void;
  appendMessage: (chatId: string, msg: UiMessage) => void;

  setRenameChatId: (id: string | null) => void;
  setDeleteChatId: (id: string | null) => void;
  setAuthError: (e: string | null) => void;

  logoutLocal: () => void;
};

export const useSession = create<SessionState>()(
  persist(
    (set, get) => ({
      username: null,
      accessToken: null,
      refreshToken: null,

      chatId: null,
      messagesByChat: {},

      renameChatId: null,
      deleteChatId: null,
      authError: null,

      setUsername: (u) => set({ username: u }),
      setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),

      setChatId: (chatId) => set({ chatId }),
      setMessagesForChat: (chatId, msgs) =>
        set((s) => ({ messagesByChat: { ...s.messagesByChat, [chatId]: msgs } })),
      appendMessage: (chatId, msg) =>
        set((s) => ({
          messagesByChat: {
            ...s.messagesByChat,
            [chatId]: [...(s.messagesByChat[chatId] ?? []), msg],
          },
        })),

      setRenameChatId: (id) => set({ renameChatId: id }),
      setDeleteChatId: (id) => set({ deleteChatId: id }),
      setAuthError: (e) => set({ authError: e }),

      logoutLocal: () =>
        set({
          username: null,
          accessToken: null,
          refreshToken: null,
          chatId: null,
          messagesByChat: {},
          renameChatId: null,
          deleteChatId: null,
          authError: null,
        }),
    }),
    {
      name: "llmchat_session_v1",
      // localStorage is default; this is just being explicit:
      // storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({
        username: s.username,
        accessToken: s.accessToken,
        refreshToken: s.refreshToken,
        chatId: s.chatId, // optional; remove if you don't want reopening last chat
      }),
    }
  )
);