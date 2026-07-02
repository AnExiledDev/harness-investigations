---
id: msg-warning-883702
name: Warning Message
category: message
subcategory: warning
source_line: 883702
---

),
            );
          return {
            kind: "raw",
            name: t.name,
            provider: "anthropic",
            baseUrl: t.base_url,
            applyAuth: async (i) => {
              i.set("Authorization", 
