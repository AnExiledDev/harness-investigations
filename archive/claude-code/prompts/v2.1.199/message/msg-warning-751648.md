---
id: msg-warning-751648
name: Warning Message
category: message
subcategory: warning
source_line: 751648
---

, "");
    for (let H of m) {
      let v = g.filter((C) => y(C, H)),
        I = h.filter(
          (C) =>
            C.source === H.source || ("plugin" in C && C.plugin === H.name),
        ),
        x =
          H.enabled === !1
            ? 
