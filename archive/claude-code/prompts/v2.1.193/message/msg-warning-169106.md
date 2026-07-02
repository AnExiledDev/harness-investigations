---
id: msg-warning-169106
name: Warning Message
category: message
subcategory: warning
source_line: 169106
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
  _truncateToLimitUtil(e, t) {
    if (e.length <= t) return e;
    return e.substring(0, t);
  }
  _isLogRecordReadonly() {
    if (this._isReadonly)
      Pae.diag.warn("Can not execute the operation on emitted log record");
    return this._isReadonly;
  }
}
var Pae, Wnt;
var eIi = E(() => {
  ((Pae = L(Oi(), 1)), (Wnt = L(Eh(), 1)));
});
class FWr {
  instrumentationScope;
  _sharedState;
  constructor(e, t) {
    ((this.instrumentationScope = e), (this._sharedState = t));
  }
  emit(e) {
    let t = e.context || tIi.context.active(),
      n = new BWr(this._sharedState, this.instrumentationScope, {
        context: t,
        ...e,
      });
    (this._sharedState.activeProcessor.onEmit(n, t), n._makeReadonly());
  }
}
var tIi;
var nIi = E(() => {
  eIi();
  tIi = L(Oi(), 1);
});
function rIi() {
  return {
    forceFlushTimeoutMillis: 30000,
    logRecordLimits: {
      attributeValueLengthLimit:
        Y2e.getNumberFromEnv("OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT") ??
        1 / 0,
      attributeCountLimit:
        Y2e.getNumberFromEnv("OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT") ?? 128,
    },
    includeTraceContext: !0,
  };
}
function oIi(e) {
  return {
    attributeCountLimit:
      e.attributeCountLimit ??
      Y2e.getNumberFromEnv("OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT") ??
      Y2e.getNumberFromEnv("OTEL_ATTRIBUTE_COUNT_LIMIT") ??
      128,
    attributeValueLengthLimit:
      e.attributeValueLengthLimit ??
      Y2e.getNumberFromEnv("OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT") ??
      Y2e.getNumberFromEnv("OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT") ??
      1 / 0,
  };
}
var Y2e;
var sIi = E(() => {
  Y2e = L(Eh(), 1);
});
class UWr {
  forceFlush() {
    return Promise.resolve();
  }
  onEmit(e, t) {}
  shutdown() {
    return Promise.resolve();
  }
}
class jWr {
  processors;
  forceFlushTimeoutMillis;
  constructor(e, t) {
    ((this.processors = e), (this.forceFlushTimeoutMillis = t));
  }
  async forceFlush() {
    let e = this.forceFlushTimeoutMillis;
    await Promise.all(
      this.processors.map((t) => iIi.callWithTimeout(t.forceFlush(), e)),
    );
  }
  onEmit(e, t) {
    this.processors.forEach((n) => n.onEmit(e, t));
  }
  async shutdown() {
    await Promise.all(this.processors.map((e) => e.shutdown()));
  }
}
var iIi;
var aIi = E(() => {
  iIi = L(Eh(), 1);
});
class GWr {
  resource;
  forceFlushTimeoutMillis;
  logRecordLimits;
  processors;
  loggers = new Map();
  activeProcessor;
  registeredLogRecordProcessors = [];
  constructor(e, t, n, r) {
    if (
      ((this.resource = e),
      (this.forceFlushTimeoutMillis = t),
      (this.logRecordLimits = n),
      (this.processors = r),
      r.length > 0)
    )
      ((this.registeredLogRecordProcessors = r),
        (this.activeProcessor = new jWr(
          this.registeredLogRecordProcessors,
          this.forceFlushTimeoutMillis,
        )));
    else this.activeProcessor = new UWr();
  }
}
var lIi = E(() => {
  aIi();
});
class X2e {
  _shutdownOnce;
  _sharedState;
  constructor(e = {}) {
    let t = Nvn.merge({}, rIi(), e),
      n = e.resource ?? cIi.defaultResource();
    ((this._sharedState = new GWr(
      n,
      t.forceFlushTimeoutMillis,
      oIi(t.logRecordLimits),
      e?.processors ?? [],
    )),
      (this._shutdownOnce = new Nvn.BindOnceFuture(this._shutdown, this)));
  }
  getLogger(e, t, n) {
    if (this._shutdownOnce.isCalled)
      return (
        $Mt.diag.warn("A shutdown LoggerProvider cannot provide a Logger"),
        DMt
      );
    if (!e)
      $Mt.diag.warn("Logger requested without instrumentation scope name.");
    let r = e || cSd,
      o = 
