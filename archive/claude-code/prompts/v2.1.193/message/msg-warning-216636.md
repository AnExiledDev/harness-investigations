---
id: msg-warning-216636
name: Warning Message
category: message
subcategory: warning
source_line: 216636
---

;
      }
    }
    let a = {
        key: "shift+enter",
        command: "workbench.action.terminal.sendSequence",
        args: { text: "\x1B\r" },
        when: "terminalFocus",
      },
      l = s.find(
        (u) => u.key === a.key && u.command === a.command && u.when === a.when,
      );
    if (l) {
      let u = Et.dim(
