---
id: msg-warning-27387
name: Warning Message
category: message
subcategory: warning
source_line: 27387
---

);
    Object.assign(a, r.def);
    let l = n.external?.defs ?? {};
    for (let c of this.seen.entries()) {
      let u = c[1];
      if (u.def && u.defId) l[u.defId] = u.def;
    }
    if (!n.external && Object.keys(l).length > 0)
      if (this.target === "draft-2020-12") a.$defs = l;
      else a.definitions = l;
    try {
      return JSON.parse(JSON.stringify(a));
    } catch (c) {
      throw Error("Error converting schema to JSON.");
    }
  }
}
function A7(e, t) {
  if (e instanceof HLt) {
    let r = new Mfn(t),
      o = {};
    for (let a of e._idmap.entries()) {
      let [l, c] = a;
      r.process(c);
    }
    let s = {},
      i = { registry: e, uri: t?.uri || ((a) => a), defs: o };
    for (let a of e._idmap.entries()) {
      let [l, c] = a;
      s[l] = r.emit(c, { ...t, external: i });
    }
    if (Object.keys(o).length > 0) {
      let a = r.target === "draft-2020-12" ? "$defs" : "definitions";
      s.__shared = { [a]: o };
    }
    return { schemas: s };
  }
  let n = new Mfn(t);
  return (n.process(e), n.emit(e, t));
}
function zD(e, t) {
  let n = t ?? { seen: new Set() };
  if (n.seen.has(e)) return !1;
  n.seen.add(e);
  let o = e._zod.def;
  switch (o.type) {
    case "string":
    case "number":
    case "bigint":
    case "boolean":
    case "date":
    case "symbol":
    case "undefined":
    case "null":
    case "any":
    case "unknown":
    case "never":
    case "void":
    case "literal":
    case "enum":
    case "nan":
    case "file":
    case "template_literal":
      return !1;
    case "array":
      return zD(o.element, n);
    case "object": {
      for (let s in o.shape) if (zD(o.shape[s], n)) return !0;
      return !1;
    }
    case "union": {
      for (let s of o.options) if (zD(s, n)) return !0;
      return !1;
    }
    case "intersection":
      return zD(o.left, n) || zD(o.right, n);
    case "tuple": {
      for (let s of o.items) if (zD(s, n)) return !0;
      if (o.rest && zD(o.rest, n)) return !0;
      return !1;
    }
    case "record":
      return zD(o.keyType, n) || zD(o.valueType, n);
    case "map":
      return zD(o.keyType, n) || zD(o.valueType, n);
    case "set":
      return zD(o.valueType, n);
    case "promise":
    case "optional":
    case "nonoptional":
    case "nullable":
    case "readonly":
      return zD(o.innerType, n);
    case "lazy":
      return zD(o.getter(), n);
    case "default":
      return zD(o.innerType, n);
    case "prefault":
      return zD(o.innerType, n);
    case "custom":
      return !1;
    case "transform":
      return !0;
    case "pipe":
      return zD(o.in, n) || zD(o.out, n);
    case "success":
      return !1;
    case "catch":
      return !1;
    default:
  }
  throw Error(
