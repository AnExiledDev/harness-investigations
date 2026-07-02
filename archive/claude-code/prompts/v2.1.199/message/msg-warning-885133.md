---
id: msg-warning-885133
name: Warning Message
category: message
subcategory: warning
source_line: 885133
---

),
        t.enforcement.fail_closed_on_error ? a(d.sub, p, "store_error") : null
      );
    }
    if (!f) return null;
    return a(d.sub, p, "over_limit", {
      cap_cents: f.cap_cents,
      source: f.scope_type,
      period: f.period,
    });
  }
  function a(d, p, f, m) {
    Fhe("spend.blocked", { request_id: p, sub: d, cause: f, ...m });
    let g =
      f === "store_error" ? "spend limit unavailable" : "spend limit reached";
    return Response.json(
      {
        type: "error",
        error: {
          type: "billing_error",
          message: n.blocked_message ? 
