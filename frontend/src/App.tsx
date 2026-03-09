import React from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatPage } from "./components/ChatPage";
import "./styles.css";
import { useSession } from "./store/session";
import { bootstrapAuth } from "./api/bootstrap";
import { isJwtExpired } from "./utils/jwt";

export default function App() {
  const { accessToken, refreshToken } = useSession();
  const [booted, setBooted] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        // Refresh only if we have refresh token AND access is missing/expired
        const needsRefresh =
          !!refreshToken && (!accessToken || isJwtExpired(accessToken));

        if (needsRefresh) {
          await bootstrapAuth();
        }
      } finally {
        if (!cancelled) setBooted(true);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []); // run once

  if (!booted) {
    // optional minimal splash; avoids a quick “logged out” flash
    return (
      <div className="bootSplash">
        <div className="bootCard">Loading…</div>
      </div>
    );
  }

  return (
    <div className="layout">
      <Sidebar />
      <ChatPage />
    </div>
  );
}