---
id: msg-warning-415046
name: Warning Message
category: message
subcategory: warning
source_line: 415046
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
var zq, QT, Tfe;
var _Qa = E(() => {
  ((zq = D(ea(), 1)), (QT = D(ey(), 1)), (Tfe = D(bre(), 1)));
});
var LHe;
var D6n = E(() => {
  (function (e) {
    ((e[(e.NOT_RECORD = 0)] = "NOT_RECORD"),
      (e[(e.RECORD = 1)] = "RECORD"),
      (e[(e.RECORD_AND_SAMPLED = 2)] = "RECORD_AND_SAMPLED"));
  })(LHe || (LHe = {}));
});
class rze {
  shouldSample() {
    return { decision: LHe.NOT_RECORD };
  }
  toString() {
    return "AlwaysOffSampler";
  }
}
var TIo = E(() => {
  D6n();
});
class DHe {
  shouldSample() {
    return { decision: LHe.RECORD_AND_SAMPLED };
  }
  toString() {
    return "AlwaysOnSampler";
  }
}
var vIo = E(() => {
  D6n();
});
class h_t {
  _root;
  _remoteParentSampled;
  _remoteParentNotSampled;
  _localParentSampled;
  _localParentNotSampled;
  constructor(e) {
    if (((this._root = e.root), !this._root))
      (bQa.globalErrorHandler(
        Error("ParentBasedSampler must have a root sampler configured"),
      ),
        (this._root = new DHe()));
    ((this._remoteParentSampled = e.remoteParentSampled ?? new DHe()),
      (this._remoteParentNotSampled = e.remoteParentNotSampled ?? new rze()),
      (this._localParentSampled = e.localParentSampled ?? new DHe()),
      (this._localParentNotSampled = e.localParentNotSampled ?? new rze()));
  }
  shouldSample(e, t, n, r, o, s) {
    let i = oze.trace.getSpanContext(e);
    if (!i || !oze.isSpanContextValid(i))
      return this._root.shouldSample(e, t, n, r, o, s);
    if (i.isRemote) {
      if (i.traceFlags & oze.TraceFlags.SAMPLED)
        return this._remoteParentSampled.shouldSample(e, t, n, r, o, s);
      return this._remoteParentNotSampled.shouldSample(e, t, n, r, o, s);
    }
    if (i.traceFlags & oze.TraceFlags.SAMPLED)
      return this._localParentSampled.shouldSample(e, t, n, r, o, s);
    return this._localParentNotSampled.shouldSample(e, t, n, r, o, s);
  }
  toString() {
    return 
