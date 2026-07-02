---
id: msg-warning-34423
name: Warning Message
category: message
subcategory: warning
source_line: 34423
---

);
  }
  function F_u(e) {
    let { schema: t, opts: n } = e;
    if (t.default !== void 0 && n.useDefaults && n.strictSchema)
      (0, Jye.checkStrictMode)(e, "default is ignored in the schema root");
  }
  function U_u(e) {
    let t = e.schema[e.opts.schemaId];
    if (t) e.baseId = (0, R_u.resolveUrl)(e.opts.uriResolver, e.baseId, t);
  }
  function j_u(e) {
    if (e.schema.$async && !e.schemaEnv.$async)
      throw Error("async schema in sync schema");
  }
  function hEs({ gen: e, schemaEnv: t, schema: n, errSchemaPath: r, opts: o }) {
    let s = n.$comment;
    if (o.$comment === !0) e.code(du._
