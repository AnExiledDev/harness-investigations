---
id: msg-warning-751342
name: Warning Message
category: message
subcategory: warning
source_line: 751342
---

,
    );
  let u = l ? (c ? { name: l, email: c } : { name: l }) : void 0,
    d = Yvc({ name: t, description: n.description, author: u, with: s }),
    p;
  try {
    let H = await Xvc(a, d, { force: n.force });
    if (!H.ok) {
      (Ie("cli_plugin_init", "target_exists"),
        r.push(
