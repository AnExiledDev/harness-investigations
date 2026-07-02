---
id: msg-warning-620683
name: Warning Message
category: message
subcategory: warning
source_line: 620683
---

,
        );
      }),
        (t[29] = p),
        (t[30] = I));
    else I = t[30];
    ((S = o.map(I)), (t[26] = p), (t[27] = o), (t[28] = S));
  } else S = t[28];
  let H;
  if (t[31] !== b || t[32] !== S)
    ((H = Jb.jsx(F, {
      marginLeft: 1,
      children: Jb.jsxs(gs, { variant: "tree", children: [b, S] }),
    })),
      (t[31] = b),
      (t[32] = S),
      (t[33] = H));
  else H = t[33];
  let v;
  if (t[34] !== H || t[35] !== h || t[36] !== _)
    ((v = Jb.jsxs(F, {
      flexDirection: "column",
      marginTop: 1,
      children: [h, _, H],
    })),
      (t[34] = H),
      (t[35] = h),
      (t[36] = _),
      (t[37] = v));
  else v = t[37];
  return v;
}
function Yzf(e) {
  return e.file;
}
function ovt() {
  let e = WWo.c(3),
    t;
  if (e[0] === Symbol.for("react.memo_cache_sentinel")) {
    let l = [
        { scope: "user", config: GT("user") },
        { scope: "project", config: GT("project") },
        { scope: "local", config: GT("local") },
        { scope: "enterprise", config: GT("enterprise") },
      ],
      c = VAo(l.filter(nKf).map(tKf));
    ((t = {
      scopes: rKf(l, {
        enterpriseActive: jP(),
        mcpLocked: cA("mcp"),
        isProjectServerApproved: eKf,
      }),
      conflicts: c,
    }),
      (e[0] = t));
  } else t = e[0];
  let { scopes: n, conflicts: r } = t,
    o = n.some(Zzf),
    s = r.length > 0 || n.some(Qzf);
  if (!o && !s) return null;
  let i;
  if (e[1] === Symbol.for("react.memo_cache_sentinel"))
    ((i = Jb.jsx(rI, {
      title: "MCP config diagnostics",
      status: o ? "error" : "warning",
    })),
      (e[1] = i));
  else i = e[1];
  let a;
  if (e[2] === Symbol.for("react.memo_cache_sentinel"))
    ((a = Jb.jsxs(F, {
      flexDirection: "column",
      marginTop: 1,
      marginBottom: 1,
      children: [
        i,
        Jb.jsx(F, {
          marginTop: 1,
          children: Jb.jsxs(w, {
            dimColor: !0,
            children: [
              "For help configuring MCP servers, see:",
              " ",
              Jb.jsx(Ds, {
                url: "https://code.claude.com/docs/en/mcp",
                children: "https://code.claude.com/docs/en/mcp",
              }),
            ],
          }),
        }),
        n.map(Jzf),
        r.length > 0 &&
          Jb.jsxs(F, {
            flexDirection: "column",
            marginTop: 1,
            children: [
              Jb.jsx(w, { color: "warning", children: "[Conflicting scopes]" }),
              Jb.jsx(gs, { variant: "tree", children: r.map(Xzf) }),
            ],
          }),
      ],
    })),
      (e[2] = a));
  else a = e[2];
  return a;
}
function Xzf(e, t) {
  return Jb.jsxs(
    gs.Group,
    {
      children: [
        Jb.jsx(gs.Node, { color: "warning", children: e.message }),
        e.suggestion &&
          Jb.jsx(gs.Node, { dimColor: !0, children: e.suggestion }),
      ],
    },
    
