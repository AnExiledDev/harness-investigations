---
id: msg-warning-721300
name: Warning Message
category: message
subcategory: warning
source_line: 721300
---

,
    );
  let u = l ? (c ? { name: l, email: c } : { name: l }) : void 0,
    d = Snc({ name: t, description: n.description, author: u, with: s }),
    p;
  try {
    let H = await Enc(a, d, { force: n.force });
    if (!H.ok) {
      (Re("cli_plugin_init", "target_exists"),
        r.push(
