---
id: msg-warning-416023
name: Warning Message
category: message
subcategory: warning
source_line: 416023
---

, { level: "warn" });
  }
  info(e, ...t) {
    return;
  }
  debug(e, ...t) {
    return;
  }
  verbose(e, ...t) {
    return;
  }
}
var YQa = "[3P telemetry] OTEL diag error:";
var XQa = E(() => {
  We();
  dr();
});
var QQa = J((F6n) => {
  Object.defineProperty(F6n, "__esModule", { value: !0 });
  F6n.OTLPExporterBase = void 0;
  class JQa {
    _delegate;
    constructor(e) {
      this._delegate = e;
    }
    export(e, t) {
      this._delegate.export(e, t);
    }
    forceFlush() {
      return this._delegate.forceFlush();
    }
    shutdown() {
      return this._delegate.shutdown();
    }
  }
  F6n.OTLPExporterBase = JQa;
});
var j6n = J((U6n) => {
  Object.defineProperty(U6n, "__esModule", { value: !0 });
  U6n.OTLPExporterError = void 0;
  class ZQa extends Error {
    code;
    name = "OTLPExporterError";
    data;
    constructor(e, t, n) {
      super(e);
      ((this.data = n), (this.code = t));
    }
  }
  U6n.OTLPExporterError = ZQa;
});
var Q6t = J((wfe) => {
  Object.defineProperty(wfe, "__esModule", { value: !0 });
  wfe.getSharedConfigurationDefaults =
    wfe.mergeOtlpSharedConfigurationWithDefaults =
    wfe.wrapStaticHeadersInFunction =
    wfe.validateTimeoutMillis =
      void 0;
  function eZa(e) {
    if (Number.isFinite(e) && e > 0) return e;
    throw Error(
      
