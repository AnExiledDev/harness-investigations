---
id: msg-warning-70302
name: Warning Message
category: message
subcategory: warning
source_line: 70302
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
    Jzu = 3000,
    Qzu = (e, { keepAlive: t, keepAliveMsecs: n }, r = Jzu) => {
      if (t !== !0) return -1;
      let o = () => {
        if (e.socket) e.socket.setKeepAlive(t, n || 0);
        else
          e.on("socket", (s) => {
            s.setKeepAlive(t, n || 0);
          });
      };
      if (r === 0) return (o(), 0);
      return e4.setTimeout(o, r);
    },
    lOs = 3000,
    Zzu = (e, t, n = 0) => {
      let r = (o) => {
        let s = n - o,
          i = () => {
            (e.destroy(),
              t(
                Object.assign(
                  Error(
                    
