---
id: msg-warning-14526
name: Warning Message
category: message
subcategory: warning
source_line: 14526
---

),
        n?.("chrome_bridge_reconnect_exhausted", { total_attempts: 100 }),
        (this.reconnectAttempts = 0));
      return;
    }
    let r = Math.min(2000 * Math.pow(1.5, this.reconnectAttempts - 1), 30000);
    if (this.reconnectAttempts <= 10 || this.reconnectAttempts % 10 === 0)
      e.info(
        
