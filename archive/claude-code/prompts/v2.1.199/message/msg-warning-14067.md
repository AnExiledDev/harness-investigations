---
id: msg-warning-14067
name: Warning Message
category: message
subcategory: warning
source_line: 14067
---

),
          r?.("chrome_bridge_handshake_timeout", {
            duration_ms: Date.now() - (this.connectionStartTime ?? 0),
            ws_state: a,
          }),
          a === void 0)
        )
          return;
        ((this.connecting = !1), this.closeSocket(), this.scheduleReconnect());
      }, qhs)));
    let o, s;
    if (n.devUserId)
      ((o = n.devUserId),
        e.debug(
