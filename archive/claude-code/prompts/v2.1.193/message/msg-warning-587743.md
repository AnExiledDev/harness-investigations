---
id: msg-warning-587743
name: Warning Message
category: message
subcategory: warning
source_line: 587743
---

,
        );
      }),
        (t[29] = p),
        (t[30] = C));
    else C = t[30];
    ((S = o.map(C)), (t[26] = p), (t[27] = o), (t[28] = S));
  } else S = t[28];
  let H;
  if (t[31] !== _ || t[32] !== S)
    ((H = db.jsx(B, {
      marginLeft: 1,
      children: db.jsxs(gs, { variant: "tree", children: [_, S] }),
    })),
      (t[31] = _),
      (t[32] = S),
      (t[33] = H));
  else H = t[33];
  let v;
  if (t[34] !== H || t[35] !== h || t[36] !== b)
    ((v = db.jsxs(B, {
      flexDirection: "column",
      marginTop: 1,
      children: [h, b, H],
    })),
      (t[34] = H),
      (t[35] = h),
      (t[36] = b),
      (t[37] = v));
  else v = t[37];
  return v;
}
function Pbf(e) {
  return e.file;
}
function B_t() {
  let e = QLo.c(3),
    t;
  if (e[0] === Symbol.for("react.memo_cache_sentinel")) {
    let l = [
        { scope: "user", config: tT("user") },
        { scope: "project", config: tT("project") },
        { scope: "local", config: tT("local") },
        { scope: "enterprise", config: tT("enterprise") },
      ],
      c = rso(l.filter(Ubf).map(Fbf));
    ((t = {
      scopes: jbf(l, {
        enterpriseActive: S1(),
        mcpLocked: EE("mcp"),
        isProjectServerApproved: Bbf,
      }),
      conflicts: c,
    }),
      (e[0] = t));
  } else t = e[0];
  let { scopes: n, conflicts: r } = t,
    o = n.some(Nbf),
    s = r.length > 0 || n.some(Obf);
  if (!o && !s) return null;
  let i;
  if (e[1] === Symbol.for("react.memo_cache_sentinel"))
    ((i = db.jsx(vI, {
      title: "MCP config diagnostics",
      status: o ? "error" : "warning",
    })),
      (e[1] = i));
  else i = e[1];
  let a;
  if (e[2] === Symbol.for("react.memo_cache_sentinel"))
    ((a = db.jsxs(B, {
      flexDirection: "column",
      marginTop: 1,
      marginBottom: 1,
      children: [
        i,
        db.jsx(B, {
          marginTop: 1,
          children: db.jsxs(w, {
            dimColor: !0,
            children: [
              "For help configuring MCP servers, see:",
              " ",
              db.jsx(Cs, {
                url: "https://code.claude.com/docs/en/mcp",
                children: "https://code.claude.com/docs/en/mcp",
              }),
            ],
          }),
        }),
        n.map($bf),
        r.length > 0 &&
          db.jsxs(B, {
            flexDirection: "column",
            marginTop: 1,
            children: [
              db.jsx(w, { color: "warning", children: "[Conflicting scopes]" }),
              db.jsx(gs, { variant: "tree", children: r.map(Mbf) }),
            ],
          }),
      ],
    })),
      (e[2] = a));
  else a = e[2];
  return a;
}
function Mbf(e, t) {
  return db.jsxs(
    gs.Group,
    {
      children: [
        db.jsx(gs.Node, { color: "warning", children: e.message }),
        e.suggestion &&
          db.jsx(gs.Node, { dimColor: !0, children: e.suggestion }),
      ],
    },
    
