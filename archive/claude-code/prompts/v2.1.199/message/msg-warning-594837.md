---
id: msg-warning-594837
name: Warning Message
category: message
subcategory: warning
source_line: 594837
---

,
    });
  }
  if (
    (q("tengu_plugin_skills_dir_loaded", {
      count: a.length,
      user_count: Fn(a, (u) => u.scope === "user"),
      project_count: Fn(a, (u) => u.scope === "project"),
      project_suppressed_count: c.length,
      error_count: o.length,
    }),
    a.length > 0)
  )
    T(
