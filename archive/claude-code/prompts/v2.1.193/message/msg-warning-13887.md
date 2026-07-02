---
id: msg-warning-13887
name: Warning Message
category: message
subcategory: warning
source_line: 13887
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
      }, AJo)));
    let o, s;
    if (n.devUserId)
      ((o = n.devUserId),
        e.debug(
