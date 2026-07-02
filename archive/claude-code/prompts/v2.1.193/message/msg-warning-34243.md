---
id: msg-warning-34243
name: Warning Message
category: message
subcategory: warning
source_line: 34243
---

);
  }
  function g5c(e) {
    let { schema: t, opts: n } = e;
    if (t.default !== void 0 && n.useDefaults && n.strictSchema)
      (0, Ome.checkStrictMode)(e, "default is ignored in the schema root");
  }
  function h5c(e) {
    let t = e.schema[e.opts.schemaId];
    if (t) e.baseId = (0, i5c.resolveUrl)(e.opts.uriResolver, e.baseId, t);
  }
  function y5c(e) {
    if (e.schema.$async && !e.schemaEnv.$async)
      throw Error("async schema in sync schema");
  }
  function Kts({ gen: e, schemaEnv: t, schema: n, errSchemaPath: r, opts: o }) {
    let s = n.$comment;
    if (o.$comment === !0) e.code(ou._
