---
id: msg-warning-216855
name: Warning Message
category: message
subcategory: warning
source_line: 216855
---

;
      }
    }
    let s;
    try {
      if (((s = Ut(r)), !Array.isArray(s))) s = [];
    } catch {
      s = [];
    }
    return (
      s.push({
        context: "Terminal",
        bindings: { "shift-enter": ["terminal::SendText", "\x1B\r"] },
      }),
      await qC.writeFile(
        n,
        Le(s, null, 2) +
          
