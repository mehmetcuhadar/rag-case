import React from "react";
import { useSession } from "../store/session";
import { sendMessage } from "../api/stream";
import { renderTextWithLinks } from "../utils/renderTextWithLinks";

export function ChatPage() {
  const { accessToken, chatId, messagesByChat, appendMessage } = useSession();
  const authed = Boolean(accessToken);

  const [prompt, setPrompt] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);

  const messages = chatId ? (messagesByChat[chatId] ?? []) : [];

  async function send() {
    if (!chatId || !prompt.trim() || isLoading) return;

    const text = prompt.trim();
    setPrompt("");
    appendMessage(chatId, { role: "user", content: text });
    setIsLoading(true);

    try {
      const res = await sendMessage(chatId, text);
      appendMessage(chatId, {
        role: "assistant",
        content: res.content ?? "",
      });
    } catch (e: any) {
      appendMessage(chatId, {
        role: "assistant",
        content: `Error: ${e.message ?? e}`,
      });
    } finally {
      setIsLoading(false);
    }
  }

  if (!authed) {
    return (
      <main className="main">
        <h1>Chat</h1>
        <div className="info">You must log in to start chat.</div>
      </main>
    );
  }

  if (!chatId) {
    return (
      <main className="main">
        <h1>Chat</h1>
        <div className="info">Create a new chat from the sidebar.</div>
      </main>
    );
  }

  return (
    <main className="main">
      <h1>Chat</h1>

      <div className="thread">
        {messages.map((m, idx) => (
          <div key={idx} className={"bubbleRow " + m.role}>
            {m.role === "assistant" ? (
              <>
                <div className="avatar assistant">🤖</div>
                <div className={"bubble " + m.role}>
                  {renderTextWithLinks(m.content)}
                </div>
                <div className="avatarSpacer" />
              </>
            ) : (
              <>
                <div className="avatarSpacer" />
                <div className={"bubble " + m.role}>{m.content}</div>
                <div className="avatar user">🧑</div>
              </>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="bubbleRow assistant">
            <div className="avatar assistant">🤖</div>
            <div className="bubble assistant">
              <div className="typing">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            </div>
            <div className="avatarSpacer" />
          </div>
        )}
      </div>

      <div className="composer">
        <input
          className="input composerInput"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Type a message"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          disabled={isLoading}
        />
        <button className="btn primary" onClick={send} disabled={isLoading || !prompt.trim()}>
          ↑
        </button>
      </div>
    </main>
  );
}