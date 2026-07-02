---
id: msg-warning-562384
name: Warning Message
category: message
subcategory: warning
source_line: 562384
---

,
    });
  }
  if (
    (V("tengu_plugin_skills_dir_loaded", {
      count: a.length,
      user_count: On(a, (u) => u.scope === "user"),
      project_count: On(a, (u) => u.scope === "project"),
      project_suppressed_count: c.length,
      error_count: o.length,
    }),
    a.length > 0)
  )
    T(
