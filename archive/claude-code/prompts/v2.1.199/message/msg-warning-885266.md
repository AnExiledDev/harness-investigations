---
id: msg-warning-885266
name: Warning Message
category: message
subcategory: warning
source_line: 885266
---

);
    return;
  }
  XAr++;
  try {
    let s = Date.now(),
      i = o.map((l) => (JAr.get(l.url)?.openUntil ?? 0) > s);
    (
      await Promise.allSettled(
        o.map((l, c) => {
          if (i[c]) return Promise.reject(Error("circuit open"));
          return Qxt(
