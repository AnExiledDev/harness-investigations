---
id: msg-warning-172267
name: Warning Message
category: message
subcategory: warning
source_line: 172267
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
      Cue.diag.warn("Can not execute the operation on emitted log record");
    return this._isReadonly;
  }
}
var Cue, Nlt;
var f3i = E(() => {
  ((Cue = D(ea(), 1)), (Nlt = D(ey(), 1)));
});
class JQr {
  instrumentationScope;
  _sharedState;
  constructor(e, t) {
    ((this.instrumentationScope = e), (this._sharedState = t));
  }
  emit(e) {
    let t = e.context || m3i.context.active(),
      n = new XQr(this._sharedState, this.instrumentationScope, {
        context: t,
        ...e,
      });
    (this._sharedState.activeProcessor.onEmit(n, t), n._makeReadonly());
  }
}
var m3i;
var g3i = E(() => {
  f3i();
  m3i = D(ea(), 1);
});
function h3i() {
  return {
    forceFlushTimeoutMillis: 30000,
    logRecordLimits: {
      attributeValueLengthLimit:
        MWe.getNumberFromEnv("OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT") ??
        1 / 0,
      attributeCountLimit:
        MWe.getNumberFromEnv("OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT") ?? 128,
    },
    includeTraceContext: !0,
  };
}
function y3i(e) {
  return {
    attributeCountLimit:
      e.attributeCountLimit ??
      MWe.getNumberFromEnv("OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT") ??
      MWe.getNumberFromEnv("OTEL_ATTRIBUTE_COUNT_LIMIT") ??
      128,
    attributeValueLengthLimit:
      e.attributeValueLengthLimit ??
      MWe.getNumberFromEnv("OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT") ??
      MWe.getNumberFromEnv("OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT") ??
      1 / 0,
  };
}
var MWe;
var _3i = E(() => {
  MWe = D(ey(), 1);
});
class QQr {
  forceFlush() {
    return Promise.resolve();
  }
  onEmit(e, t) {}
  shutdown() {
    return Promise.resolve();
  }
}
class ZQr {
  processors;
  forceFlushTimeoutMillis;
  constructor(e, t) {
    ((this.processors = e), (this.forceFlushTimeoutMillis = t));
  }
  async forceFlush() {
    let e = this.forceFlushTimeoutMillis;
    await Promise.all(
      this.processors.map((t) => b3i.callWithTimeout(t.forceFlush(), e)),
    );
  }
  onEmit(e, t) {
    this.processors.forEach((n) => n.onEmit(e, t));
  }
  async shutdown() {
    await Promise.all(this.processors.map((e) => e.shutdown()));
  }
}
var b3i;
var S3i = E(() => {
  b3i = D(ey(), 1);
});
class eZr {
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
        (this.activeProcessor = new ZQr(
          this.registeredLogRecordProcessors,
          this.forceFlushTimeoutMillis,
        )));
    else this.activeProcessor = new QQr();
  }
}
var E3i = E(() => {
  S3i();
});
class $We {
  _shutdownOnce;
  _sharedState;
  constructor(e = {}) {
    let t = WDn.merge({}, h3i(), e),
      n = e.resource ?? A3i.defaultResource();
    ((this._sharedState = new eZr(
      n,
      t.forceFlushTimeoutMillis,
      y3i(t.logRecordLimits),
      e?.processors ?? [],
    )),
      (this._shutdownOnce = new WDn.BindOnceFuture(this._shutdown, this)));
  }
  getLogger(e, t, n) {
    if (this._shutdownOnce.isCalled)
      return (
        t2t.diag.warn("A shutdown LoggerProvider cannot provide a Logger"),
        QUt
      );
    if (!e)
      t2t.diag.warn("Logger requested without instrumentation scope name.");
    let r = e || U9d,
      o = 
