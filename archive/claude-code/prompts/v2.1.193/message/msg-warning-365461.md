---
id: msg-warning-365461
name: Warning Message
category: message
subcategory: warning
source_line: 365461
---

),
        e
      );
    if (typeof e === "string") return this._truncateToLimitUtil(e, t);
    if (Array.isArray(e))
      return e.map((n) =>
        typeof n === "string" ? this._truncateToLimitUtil(n, t) : n,
      );
    return e;
  }
}
var $W, lT, aue;
var FRa = E(() => {
  (($W = L(Oi(), 1)), (lT = L(Eh(), 1)), (aue = L(Iee(), 1)));
});
var Gbe;
var XFn = E(() => {
  (function (e) {
    ((e[(e.NOT_RECORD = 0)] = "NOT_RECORD"),
      (e[(e.RECORD = 1)] = "RECORD"),
      (e[(e.RECORD_AND_SAMPLED = 2)] = "RECORD_AND_SAMPLED"));
  })(Gbe || (Gbe = {}));
});
class a5e {
  shouldSample() {
    return { decision: Gbe.NOT_RECORD };
  }
  toString() {
    return "AlwaysOffSampler";
  }
}
var cdo = E(() => {
  XFn();
});
class Wbe {
  shouldSample() {
    return { decision: Gbe.RECORD_AND_SAMPLED };
  }
  toString() {
    return "AlwaysOnSampler";
  }
}
var udo = E(() => {
  XFn();
});
class ydt {
  _root;
  _remoteParentSampled;
  _remoteParentNotSampled;
  _localParentSampled;
  _localParentNotSampled;
  constructor(e) {
    if (((this._root = e.root), !this._root))
      (URa.globalErrorHandler(
        Error("ParentBasedSampler must have a root sampler configured"),
      ),
        (this._root = new Wbe()));
    ((this._remoteParentSampled = e.remoteParentSampled ?? new Wbe()),
      (this._remoteParentNotSampled = e.remoteParentNotSampled ?? new a5e()),
      (this._localParentSampled = e.localParentSampled ?? new Wbe()),
      (this._localParentNotSampled = e.localParentNotSampled ?? new a5e()));
  }
  shouldSample(e, t, n, r, o, s) {
    let i = l5e.trace.getSpanContext(e);
    if (!i || !l5e.isSpanContextValid(i))
      return this._root.shouldSample(e, t, n, r, o, s);
    if (i.isRemote) {
      if (i.traceFlags & l5e.TraceFlags.SAMPLED)
        return this._remoteParentSampled.shouldSample(e, t, n, r, o, s);
      return this._remoteParentNotSampled.shouldSample(e, t, n, r, o, s);
    }
    if (i.traceFlags & l5e.TraceFlags.SAMPLED)
      return this._localParentSampled.shouldSample(e, t, n, r, o, s);
    return this._localParentNotSampled.shouldSample(e, t, n, r, o, s);
  }
  toString() {
    return 
