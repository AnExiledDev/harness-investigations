---
id: msg-warning-36240
name: Warning Message
category: message
subcategory: warning
source_line: 36240
---

));
  }
  function gSu(e) {
    let { metaSchema: t } = e;
    if (t === void 0) return;
    if (e.$data && this.opts.$data) t = XEs(t);
    e.validateSchema = this.compile(t, !0);
  }
  var hSu = {
    $ref: "https://raw.githubusercontent.com/ajv-validator/ajv/master/lib/refs/data.json#",
  };
  function XEs(e) {
    return { anyOf: [e, hSu] };
  }
});
var QEs = J((rDr) => {
  Object.defineProperty(rDr, "__esModule", { value: !0 });
  var ySu = {
    keyword: "id",
    code() {
      throw Error('NOT SUPPORTED: keyword "id", use "$id" for schema ID');
    },
  };
  rDr.default = ySu;
});
var nAs = J((yje) => {
  Object.defineProperty(yje, "__esModule", { value: !0 });
  yje.callRef = yje.getValidate = void 0;
  var _Su = NDt(),
    ZEs = C7(),
    dW = vm(),
    dnt = Xye(),
    eAs = zmn(),
    Zmn = xy(),
    bSu = {
      keyword: "$ref",
      schemaType: "string",
      code(e) {
        let { gen: t, schema: n, it: r } = e,
          { baseId: o, schemaEnv: s, validateName: i, opts: a, self: l } = r,
          { root: c } = s;
        if ((n === "#" || n === "#/") && o === c.baseId) return d();
        let u = eAs.resolveRef.call(l, c, o, n);
        if (u === void 0) throw new _Su.default(r.opts.uriResolver, o, n);
        if (u instanceof eAs.SchemaEnv) return p(u);
        return f(u);
        function d() {
          if (s === c) return egn(e, i, s, s.$async);
          let m = t.scopeValue("root", { ref: c });
          return egn(e, dW._
