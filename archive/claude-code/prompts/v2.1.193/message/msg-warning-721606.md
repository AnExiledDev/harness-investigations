---
id: msg-warning-721606
name: Warning Message
category: message
subcategory: warning
source_line: 721606
---

, "");
    for (let H of m) {
      let v = g.filter((I) => y(I, H)),
        C = h.filter(
          (I) =>
            I.source === H.source || ("plugin" in I && I.plugin === H.name),
        ),
        x =
          H.enabled === !1
            ? 
