---
id: msg-warning-555868
name: Warning Message
category: message
subcategory: warning
source_line: 555868
---

,
                          { level: "warn" },
                        );
                      return p;
                    } else if (d.isFile() && c.endsWith(".md")) {
                      if (rZ(u, c, i)) return [];
                      let p = await u.readFile(c, { encoding: "utf-8" }),
                        { frontmatter: f, content: m } = Gm(p, c, {
                          normalizeKeys: !0,
                        }),
                        g,
                        h;
                      if (s.commandsMetadata) {
                        for (let [S, H] of Object.entries(s.commandsMetadata))
                          if (H.source) {
                            let v = uk.join(s.path, H.source);
                            if (c === v) {
                              ((g = 
