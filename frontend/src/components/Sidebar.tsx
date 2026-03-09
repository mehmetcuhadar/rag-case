import React from "react";
import { login, register, logout } from "../api/auth";
import { createChat, listChats, getMessages, renameChat, deleteChat } from "../api/chats";
import { useSession } from "../store/session";

export function Sidebar() {
  const {
    username, accessToken, chatId,
    setChatId, setMessagesForChat,
    renameChatId, setRenameChatId,
    deleteChatId, setDeleteChatId,
    authError, setAuthError,
  } = useSession();

  const authed = Boolean(accessToken);

  const [u, setU] = React.useState("mehmet");
  const [p, setP] = React.useState("");

  const [chats, setChats] = React.useState<{ chat_id: string; chat_name?: string | null }[]>([]);
  const [loadingChats, setLoadingChats] = React.useState(false);

  async function reloadChats() {
    if (!authed) return;
    setLoadingChats(true);
    try {
      const rows = await listChats();
      setChats(rows);
    } catch (e: any) {
      setChats([]);
    } finally {
      setLoadingChats(false);
    }
  }

  React.useEffect(() => {
    reloadChats();
  }, [authed]);

  async function selectChat(id: string) {
    setChatId(id);
    const msgs = await getMessages(id, 200);
    setMessagesForChat(id, msgs.map(m => ({ role: m.role, content: m.content })));
  }

  async function onNewChat() {
    const c = await createChat("New chat");
    await reloadChats();
    setChatId(c.chat_id);
    setMessagesForChat(c.chat_id, []);
  }

  return (
    <aside className="sidebar">
      <div className="section">
        <div className="sectionTitle">Account</div>

        {!authed ? (
          <>
            <label className="label">Username</label>
            <input className="input" value={u} onChange={(e) => setU(e.target.value)} placeholder="mehmet" />
            <label className="label">Password</label>
            <input className="input" value={p} onChange={(e) => setP(e.target.value)} type="password" />

            {authError ? <div className="error">{authError}</div> : null}

            <div className="row2">
              <button
                className="btn primary"
                onClick={async () => {
                  setAuthError(null);
                  try {
                    if (!u.trim() || !p) throw new Error("Username and password required.");
                    await login(u.trim(), p);
                    await reloadChats();
                  } catch (e: any) {
                    setAuthError(e.message ?? "Login failed.");
                  }
                }}
              >
                Login
              </button>

              <button
                className="btn"
                onClick={async () => {
                  setAuthError(null);
                  try {
                    if (!u.trim() || !p) throw new Error("Username and password required.");
                    await register(u.trim(), p);
                    await reloadChats();
                  } catch (e: any) {
                    setAuthError(e.message ?? "Register failed.");
                  }
                }}
              >
                Register
              </button>
            </div>

            <div className="divider" />
            <div className="caption">Login to see your chats.</div>
          </>
        ) : (
          <>
            <div className="caption">Signed in as: <b>{username ?? ""}</b></div>
            <button
              className="btn"
              onClick={async () => {
                await logout();
                setChats([]);
              }}
            >
              Logout
            </button>
          </>
        )}
      </div>

      <div className="divider" />

      <div className="section">
        <div className="rowBetween">
          <div className="sectionTitle">Chats</div>
          <button className="btn small" onClick={onNewChat} disabled={!authed}>＋</button>
        </div>

        {loadingChats ? <div className="caption">Loading…</div> : null}

        <div className="chatList">
          {chats.map((c) => {
            const id = c.chat_id;
            const label = (c.chat_name ?? "Untitled").trim();
            const selected = chatId === id;
            const renaming = renameChatId === id;
            const deleting = deleteChatId === id;

            return (
              <div key={id} className="chatRow">
                <button className={"chatBtn " + (selected ? "selected" : "")} onClick={() => selectChat(id)}>
                  {selected ? `▸ ${label}` : label}
                </button>

                <button
                  className="iconBtn"
                  title="Rename"
                  onClick={() => setRenameChatId(renaming ? null : id)}
                >
                  🖊️
                </button>

                <button
                  className="iconBtn"
                  title="Delete"
                  onClick={() => setDeleteChatId(deleting ? null : id)}
                >
                  🗑️
                </button>

                {renaming ? (
                  <RenameInline
                    initial={label}
                    onSave={async (nn) => {
                      if (nn.trim()) await renameChat(id, nn.trim());
                      setRenameChatId(null);
                      await reloadChats();
                    }}
                    onCancel={() => setRenameChatId(null)}
                  />
                ) : null}

                {deleting ? (
                  <DeleteInline
                    onConfirm={async () => {
                      await deleteChat(id);
                      setDeleteChatId(null);
                      await reloadChats();
                      // if deleting current chat:
                      if (useSession.getState().chatId === id) {
                        useSession.getState().setChatId(null);
                      }
                    }}
                    onCancel={() => setDeleteChatId(null)}
                  />
                ) : null}
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
}

function RenameInline(props: { initial: string; onSave: (v: string) => void; onCancel: () => void }) {
  const [v, setV] = React.useState(props.initial);
  return (
    <div className="inlineBox">
      <input className="input" value={v} onChange={(e) => setV(e.target.value)} />
      <div className="row2">
        <button className="btn primary" onClick={() => props.onSave(v)}>Save</button>
        <button className="btn" onClick={props.onCancel}>Cancel</button>
      </div>
    </div>
  );
}

function DeleteInline(props: { onConfirm: () => void; onCancel: () => void }) {
  return (
    <div className="inlineBox">
      <div className="warn">Delete this chat?</div>
      <div className="row2">
        <button className="btn primary" onClick={props.onConfirm}>Delete</button>
        <button className="btn" onClick={props.onCancel}>Cancel</button>
      </div>
    </div>
  );
}