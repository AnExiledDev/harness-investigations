---
id: msg-warning-4691
name: Warning Message
category: message
subcategory: warning
source_line: 4691
---

)) {
  if (typeof process > "u") return;
  let n = await import("fs"),
    r = e,
    o;
  try {
    ((r = await n.promises.realpath(e)), (o = await n.promises.stat(r)));
  } catch {
    return;
  }
  let s = o.mode & 511;
  if (s & 18)
    throw new Jp(
      
