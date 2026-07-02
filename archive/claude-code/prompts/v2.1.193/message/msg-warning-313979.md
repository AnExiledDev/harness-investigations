---
id: msg-warning-313979
name: Warning Message
category: message
subcategory: warning
source_line: 313979
---


        : null,
    l;
  if (Array.isArray(o)) {
    let c = o.map((u, d) => {
      if (u.type === "image")
        return qb.jsx(
          B,
          {
            justifyContent: "space-between",
            overflowX: "hidden",
            width: "100%",
            children: qb.jsx(qn, {
              height: 1,
              children: qb.jsx(w, { children: "[Image]" }),
            }),
          },
          d,
        );
      return qb.jsx(mtp, { item: u, verbose: n }, d);
    });
    l = qb.jsx(B, { flexDirection: "column", width: "100%", children: c });
  } else if (!o)
    l = qb.jsx(B, {
      justifyContent: "space-between",
      overflowX: "hidden",
      width: "100%",
      children: qb.jsx(qn, {
        height: 1,
        children: qb.jsx(w, { dimColor: !0, children: "(No content)" }),
      }),
    });
  else l = qb.jsx(_1, { content: o, verbose: n });
  if (a)
    return qb.jsxs(B, {
      flexDirection: "column",
      children: [
        qb.jsx(qn, {
          height: 1,
          children: qb.jsx(w, { color: "warning", children: a }),
        }),
        l,
      ],
    });
  return l;
}
function mtp(e) {
  let t = Iua.c(7),
    { item: n, verbose: r } = e,
    o =
      n.type === "text" && "text" in n && n.text !== null && n.text !== void 0
        ? String(n.text)
        : "",
    s;
  if (t[4] !== o || t[5] !== r)
    ((s = qb.jsx(_1, { content: o, verbose: r })),
      (t[4] = o),
      (t[5] = r),
      (t[6] = s));
  else s = t[6];
  return s;
}
function gtp(e, { maxChars: t, maxKeys: n }) {
  let r = e.trim();
  if (r.length === 0 || r.length > t || r[0] !== "{") return null;
  let o;
  try {
    o = Ut(r);
  } catch {
    return null;
  }
  if (o === null || typeof o !== "object" || Array.isArray(o)) return null;
  let s = Object.entries(o);
  if (s.length === 0 || s.length > n) return null;
  return s;
}
function ytp(e, t) {
  let n = e;
  if (Array.isArray(e)) {
    let c = e.find((u) => u.type === "text");
    n = c && "text" in c ? c.text : void 0;
  }
  if (typeof n !== "string" || !n.includes('"message_link"')) return null;
  let o = gtp(n, { maxChars: 2000, maxKeys: 6 })?.find(
    ([c]) => c === "message_link",
  )?.[1];
  if (typeof o !== "string") return null;
  let s = htp.exec(o);
  if (!s) return null;
  let i = t,
    a = i?.channel_id ?? i?.channel ?? s[1],
    l = typeof a === "string" && a ? a : "slack";
  return { channel: l.startsWith("#") ? l : 
