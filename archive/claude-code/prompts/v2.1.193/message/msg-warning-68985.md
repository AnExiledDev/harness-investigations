---
id: msg-warning-68985
name: Warning Message
category: message
subcategory: warning
source_line: 68985
---

;
          if (r) {
            let i = Object.assign(Error(s), {
              name: "TimeoutError",
              code: "ETIMEDOUT",
            });
            (e.destroy(i), t(i));
          } else
            ((s +=
              " Init client requestHandler with throwOnRequestTimeout=true to turn this into an error."),
              o?.warn?.(s));
        }, n);
      return -1;
    },
    BAu = 3000,
    FAu = (e, { keepAlive: t, keepAliveMsecs: n }, r = BAu) => {
      if (t !== !0) return -1;
      let o = () => {
        if (e.socket) e.socket.setKeepAlive(t, n || 0);
        else
          e.on("socket", (s) => {
            s.setKeepAlive(t, n || 0);
          });
      };
      if (r === 0) return (o(), 0);
      return b2.setTimeout(o, r);
    },
    __s = 3000,
    UAu = (e, t, n = 0) => {
      let r = (o) => {
        let s = n - o,
          i = () => {
            (e.destroy(),
              t(
                Object.assign(
                  Error(
                    
