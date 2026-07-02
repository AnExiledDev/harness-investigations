---
id: msg-warning-172224
name: Warning Message
category: message
subcategory: warning
source_line: 172224
---

), this);
    if (
      !Nlt.isAttributeValue(t) &&
      !(typeof t === "object" && !Array.isArray(t) && Object.keys(t).length > 0)
    )
      return (Cue.diag.warn(
