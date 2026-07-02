---
id: msg-warning-284853
name: Warning Message
category: message
subcategory: warning
source_line: 284853
---

,
        { level: "warn" },
      );
    }
  for await (let o of d5t(e, void 0, void 0, t)) {
    if (
      o.message &&
      !(
        o.message.type === "attachment" &&
        o.message.attachment.type === "hook_blocking_error"
      )
    )
      n.push(o.message);
    if (o.blockingError) n.push(Nft("Setup", o.blockingError, 
