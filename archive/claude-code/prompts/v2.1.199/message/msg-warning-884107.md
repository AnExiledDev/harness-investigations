---
id: msg-warning-884107
name: Warning Message
category: message
subcategory: warning
source_line: 884107
---

),
        xUe(f, ftu(f), ptu[f] ?? "upstream error", a)
      );
    }
    throw p;
  }
}
function ftu(e) {
  return (e !== void 0 && yXm[e]) || "api_error";
}
function tcs(e, t, n, r) {
  let o = new Map();
  for (let s of e)
    o.set(s.id, {
      type: "model",
      id: s.id,
      display_name: s.label ?? s.id,
      ...(s.description && { description: s.description }),
    });
  if (n) {
    let s = [qne, jW, Vne],
      i = _Xm.filter((a) => !s.includes(a)).reverse();
    for (let a of [...s, ...i]) {
      let l = La[a];
      if (o.has(l.firstParty)) continue;
      let c = !1;
      for (let u of t)
        if (u === "anthropic" || l[u] !== null) {
          c = !0;
          break;
        }
      if (c)
        o.set(l.firstParty, {
          type: "model",
          id: l.firstParty,
          display_name: l.firstParty,
        });
    }
  }
  return r ? [...o.values()].filter((s) => Zls(s.id, r)) : [...o.values()];
}
function mtu(e, t, n = !0, r) {
  return Response.json({
    data: tcs(e, new Set(t.map((o) => o.provider)), n, r),
    has_more: !1,
    first_id: null,
    last_id: null,
  });
}
var iXm,
  lXm,
  cXm,
  uXm,
  zAr = 3600000,
  yXm,
  ptu,
  _Xm;
var ncs = E(() => {
  qM();
  m$();
  Rc();
  ut();
  f$();
  Ao();
  Wg();
  Zt();
  Ete();
  Zxt();
  itu();
  iXm = new Set([
    "content-type",
    "accept",
    "accept-encoding",
    "anthropic-beta",
    "anthropic-version",
    "user-agent",
  ]);
  ((lXm = [
    "content-encoding",
    "content-length",
    "transfer-encoding",
    "connection",
    "cf-ray",
    "via",
    "request-id",
  ]),
    (cXm = {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    }),
    (uXm = ["/v1/messages", "/v1/messages/count_tokens"]));
  ((yXm = {
    400: "invalid_request_error",
    401: "authentication_error",
    403: "permission_error",
    404: "not_found_error",
    429: "rate_limit_error",
    529: "overloaded_error",
  }),
    (ptu = {
      400: "upstream rejected the request",
      401: "upstream authentication failed \u2014 check the gateway operator",
      403: "upstream denied the request \u2014 check the gateway operator",
      404: "upstream resource not found",
      429: "upstream rate limit exceeded",
      500: "upstream error",
      529: "upstream overloaded",
    }));
  _Xm = [
    "haiku45",
    "sonnet45",
    "sonnet46",
    "sonnet5",
    "opus41",
    "opus46",
    "opus47",
    "opus48",
    "fable5",
  ];
});
function Vw(e, t, n) {
  return Response.json(
    { type: "error", error: { type: bXm[e], message: t }, request_id: n },
    { status: e },
  );
}
function Jan(e, t) {
  let n = Number(e.get("limit") ?? t);
  if (!Number.isInteger(n) || n < 1 || n > 1000) return null;
  return n;
}
var uZe, bXm;
var rcs = E(() => {
  ((uZe = { "Cache-Control": "no-store" }),
    (bXm = {
      400: "invalid_request_error",
      401: "authentication_error",
      403: "permission_error",
      404: "not_found_error",
    }));
});
function Zan(e = "monthly", t = new Date()) {
  if (e === "monthly") return t.toISOString().slice(0, 7);
  if (e === "daily") return t.toISOString().slice(0, 10);
  let n = new Date(
      Date.UTC(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate()),
    ),
    r = n.getUTCDay() || 7;
  n.setUTCDate(n.getUTCDate() + 4 - r);
  let o = n.getUTCFullYear(),
    s = Date.UTC(o, 0, 1),
    i = Math.ceil(((n.getTime() - s) / 86400000 + 1) / 7);
  return 
