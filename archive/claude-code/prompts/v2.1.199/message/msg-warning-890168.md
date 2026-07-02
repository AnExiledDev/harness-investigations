---
id: msg-warning-890168
name: Warning Message
category: message
subcategory: warning
source_line: 890168
---

,
                  );
                return ks;
              })
            : Promise.resolve({});
        if (
          Y8c({
            remote: fe,
            isNonInteractiveSession: Ye,
            isContinue: Boolean(a.continue),
            pendingAssistantChat: void 0,
            pendingConnectUrl: knu?.url,
            pendingSSHHost: vcs?.host,
          })
        )
          S2e(!0);
        T("[STARTUP] Loading MCP configs...");
        let wn = Date.now(),
          cr,
          Ot = (
            Wr || Dd() || ta() ? Promise.resolve({ servers: {} }) : WQ(it)
          ).then((Xn) => ((cr = Date.now() - wn), Xn)),
          fn = Ad();
        if (R && R !== "text" && R !== "stream-json")
          return Ts(
