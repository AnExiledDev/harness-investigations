---
id: msg-warning-284799
name: Warning Message
category: message
subcategory: warning
source_line: 284799
---

,
        { level: "error" },
      );
    }
  let d = r ?? u1();
  for await (let p of u5t(e, t, n, d, o, void 0, void 0, s)) {
    if (
      p.message &&
      !(
        p.message.type === "attachment" &&
        p.message.attachment.type === "hook_blocking_error"
      )
    )
      i.push(p.message);
    if (p.blockingError)
      i.push(Nft("SessionStart", p.blockingError, 
