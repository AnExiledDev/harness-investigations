---
id: msg-warning-220164
name: Warning Message
category: message
subcategory: warning
source_line: 220164
---

;
      }
    }
    let s;
    try {
      if (((s = Gt(r)), !Array.isArray(s))) s = [];
    } catch {
      s = [];
    }
    return (
      s.push({
        context: "Terminal",
        bindings: { "shift-enter": ["terminal::SendText", "\x1B\r"] },
      }),
      await sx.writeFile(
        n,
        ke(s, null, 2) +
          
