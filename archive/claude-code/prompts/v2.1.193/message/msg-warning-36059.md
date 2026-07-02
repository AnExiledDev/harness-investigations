---
id: msg-warning-36059
name: Warning Message
category: message
subcategory: warning
source_line: 36059
---

));
  }
  function WVc(e) {
    let { metaSchema: t } = e;
    if (t === void 0) return;
    if (e.$data && this.opts.$data) t = Ins(t);
    e.validateSchema = this.compile(t, !0);
  }
  var VVc = {
    $ref: "https://raw.githubusercontent.com/ajv-validator/ajv/master/lib/refs/data.json#",
  };
  function Ins(e) {
    return { anyOf: [e, VVc] };
  }
});
var kns = Q((pEr) => {
  Object.defineProperty(pEr, "__esModule", { value: !0 });
  var qVc = {
    keyword: "id",
    code() {
      throw Error('NOT SUPPORTED: keyword "id", use "$id" for schema ID');
    },
  };
  pEr.default = qVc;
});
var Pns = Q((BNe) => {
  Object.defineProperty(BNe, "__esModule", { value: !0 });
  BNe.callRef = BNe.getValidate = void 0;
  var zVc = $Ct(),
    Rns = Zz(),
    y3 = Jf(),
    mXe = $me(),
    Lns = ein(),
    iin = Zh(),
    KVc = {
      keyword: "$ref",
      schemaType: "string",
      code(e) {
        let { gen: t, schema: n, it: r } = e,
          { baseId: o, schemaEnv: s, validateName: i, opts: a, self: l } = r,
          { root: c } = s;
        if ((n === "#" || n === "#/") && o === c.baseId) return d();
        let u = Lns.resolveRef.call(l, c, o, n);
        if (u === void 0) throw new zVc.default(r.opts.uriResolver, o, n);
        if (u instanceof Lns.SchemaEnv) return p(u);
        return f(u);
        function d() {
          if (s === c) return ain(e, i, s, s.$async);
          let m = t.scopeValue("root", { ref: c });
          return ain(e, y3._
