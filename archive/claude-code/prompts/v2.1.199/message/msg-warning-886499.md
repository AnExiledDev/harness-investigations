---
id: msg-warning-886499
name: Warning Message
category: message
subcategory: warning
source_line: 886499
---

);
      if (a && U === "/v1/messages") {
        let ie = re;
        return a.meter(
          ee,
          X,
          oe,
          ie ? () => ltu(ie, _, t.models, t.auto_include_builtin_models) : null,
          se,
        );
      }
      return ee;
    }
    return new Response("not found", { status: 404 });
  }
  let P = Bun.serve({
    hostname: t.listen.host,
    port: t.listen.port,
    idleTimeout: 0,
    development: !1,
    ...(S && { tls: S }),
    fetch: async (M, R) => {
      let O = Keu(R.requestIP(M)?.address, M.headers.get("x-forwarded-for"), n),
        j = mJm(M),
        $;
      try {
        $ = await L(M, O, j);
      } catch (N) {
        (Tu("error", 
