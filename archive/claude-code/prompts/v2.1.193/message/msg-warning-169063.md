---
id: msg-warning-169063
name: Warning Message
category: message
subcategory: warning
source_line: 169063
---

), this);
    if (
      !Wnt.isAttributeValue(t) &&
      !(typeof t === "object" && !Array.isArray(t) && Object.keys(t).length > 0)
    )
      return (Pae.diag.warn(
