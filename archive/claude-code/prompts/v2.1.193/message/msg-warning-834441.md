---
id: msg-warning-834441
name: Warning Message
category: message
subcategory: warning
source_line: 834441
---

,
                  );
                return hs;
              })
            : Promise.resolve({});
        if (
          NIc({
            remote: pe,
            isNonInteractiveSession: we,
            isContinue: Boolean(a.continue),
            pendingAssistantChat: void 0,
            pendingConnectUrl: QLc?.url,
            pendingSSHHost: i8o?.host,
          })
        )
          j1e(!0);
        T("[STARTUP] Loading MCP configs...");
        let _t = Date.now(),
          cn,
          Ke = (
            Jt || cd() || sa() ? Promise.resolve({ servers: {} }) : nX(ze)
          ).then((Jn) => ((cn = Date.now() - _t), Jn)),
          Dt = td();
        if (D && D !== "text" && D !== "stream-json")
          return vs(
