---
id: msg-warning-366438
name: Warning Message
category: message
subcategory: warning
source_line: 366438
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
var yLa = "[3P telemetry] OTEL diag error:";
var _La = E(() => {
  Ge();
  kr();
});
var SLa = Q((rUn) => {
  Object.defineProperty(rUn, "__esModule", { value: !0 });
  rUn.OTLPExporterBase = void 0;
  class bLa {
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
  rUn.OTLPExporterBase = bLa;
});
var sUn = Q((oUn) => {
  Object.defineProperty(oUn, "__esModule", { value: !0 });
  oUn.OTLPExporterError = void 0;
  class ELa extends Error {
    code;
    name = "OTLPExporterError";
    data;
    constructor(e, t, n) {
      super(e);
      ((this.data = n), (this.code = t));
    }
  }
  oUn.OTLPExporterError = ELa;
});
var V4t = Q((cue) => {
  Object.defineProperty(cue, "__esModule", { value: !0 });
  cue.getSharedConfigurationDefaults =
    cue.mergeOtlpSharedConfigurationWithDefaults =
    cue.wrapStaticHeadersInFunction =
    cue.validateTimeoutMillis =
      void 0;
  function HLa(e) {
    if (Number.isFinite(e) && e > 0) return e;
    throw Error(
      
