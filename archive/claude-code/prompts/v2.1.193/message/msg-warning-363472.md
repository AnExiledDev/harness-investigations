---
id: msg-warning-363472
name: Warning Message
category: message
subcategory: warning
source_line: 363472
---

),
        x_.DROP_AGGREGATION
      );
    }
    createAggregator(e) {
      return this._resolve(e).createAggregator(e);
    }
  }
  x_.DefaultAggregation = Yuo;
  x_.DROP_AGGREGATION = new bFn();
  x_.SUM_AGGREGATION = new M4t();
  x_.LAST_VALUE_AGGREGATION = new SFn();
  x_.HISTOGRAM_AGGREGATION = new EFn();
  x_.EXPONENTIAL_HISTOGRAM_AGGREGATION = new Kuo();
  x_.DEFAULT_AGGREGATION = new Yuo();
});
var $4t = Q((r5e) => {
  Object.defineProperty(r5e, "__esModule", { value: !0 });
  r5e.toAggregation = r5e.AggregationType = void 0;
  var t5e = S0a(),
    n5e;
  (function (e) {
    ((e[(e.DEFAULT = 0)] = "DEFAULT"),
      (e[(e.DROP = 1)] = "DROP"),
      (e[(e.SUM = 2)] = "SUM"),
      (e[(e.LAST_VALUE = 3)] = "LAST_VALUE"),
      (e[(e.EXPLICIT_BUCKET_HISTOGRAM = 4)] = "EXPLICIT_BUCKET_HISTOGRAM"),
      (e[(e.EXPONENTIAL_HISTOGRAM = 5)] = "EXPONENTIAL_HISTOGRAM"));
  })((n5e = r5e.AggregationType || (r5e.AggregationType = {})));
  function Xbp(e) {
    switch (e.type) {
      case n5e.DEFAULT:
        return t5e.DEFAULT_AGGREGATION;
      case n5e.DROP:
        return t5e.DROP_AGGREGATION;
      case n5e.SUM:
        return t5e.SUM_AGGREGATION;
      case n5e.LAST_VALUE:
        return t5e.LAST_VALUE_AGGREGATION;
      case n5e.EXPONENTIAL_HISTOGRAM: {
        let t = e;
        return new t5e.ExponentialHistogramAggregation(
          t.options?.maxSize,
          t.options?.recordMinMax,
        );
      }
      case n5e.EXPLICIT_BUCKET_HISTOGRAM: {
        let t = e;
        if (t.options == null) return t5e.HISTOGRAM_AGGREGATION;
        else
          return new t5e.ExplicitBucketHistogramAggregation(
            t.options?.boundaries,
            t.options?.recordMinMax,
          );
      }
      default:
        throw Error("Unsupported Aggregation");
    }
  }
  r5e.toAggregation = Xbp;
});
var Xuo = Q((cdt) => {
  Object.defineProperty(cdt, "__esModule", { value: !0 });
  cdt.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR =
    cdt.DEFAULT_AGGREGATION_SELECTOR = void 0;
  var Jbp = lFn(),
    Qbp = $4t(),
    Zbp = (e) => ({ type: Qbp.AggregationType.DEFAULT });
  cdt.DEFAULT_AGGREGATION_SELECTOR = Zbp;
  var eSp = (e) => Jbp.AggregationTemporality.CUMULATIVE;
  cdt.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR = eSp;
});
var Juo = Q((AFn) => {
  Object.defineProperty(AFn, "__esModule", { value: !0 });
  AFn.MetricReader = void 0;
  var E0a = Oi(),
    HFn = Dne(),
    H0a = Xuo();
  class A0a {
    _shutdown = !1;
    _metricProducers;
    _sdkMetricProducer;
    _aggregationTemporalitySelector;
    _aggregationSelector;
    _cardinalitySelector;
    constructor(e) {
      ((this._aggregationSelector =
        e?.aggregationSelector ?? H0a.DEFAULT_AGGREGATION_SELECTOR),
        (this._aggregationTemporalitySelector =
          e?.aggregationTemporalitySelector ??
          H0a.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR),
        (this._metricProducers = e?.metricProducers ?? []),
        (this._cardinalitySelector = e?.cardinalitySelector));
    }
    setMetricProducer(e) {
      if (this._sdkMetricProducer)
        throw Error("MetricReader can not be bound to a MeterProvider again.");
      ((this._sdkMetricProducer = e), this.onInitialized());
    }
    selectAggregation(e) {
      return this._aggregationSelector(e);
    }
    selectAggregationTemporality(e) {
      return this._aggregationTemporalitySelector(e);
    }
    selectCardinalityLimit(e) {
      return this._cardinalitySelector ? this._cardinalitySelector(e) : 2000;
    }
    onInitialized() {}
    async collect(e) {
      if (this._sdkMetricProducer === void 0)
        throw Error("MetricReader is not bound to a MetricProducer");
      if (this._shutdown) throw Error("MetricReader is shutdown");
      let [t, ...n] = await Promise.all([
          this._sdkMetricProducer.collect({ timeoutMillis: e?.timeoutMillis }),
          ...this._metricProducers.map((i) =>
            i.collect({ timeoutMillis: e?.timeoutMillis }),
          ),
        ]),
        r = t.errors.concat((0, HFn.FlatMap)(n, (i) => i.errors)),
        o = t.resourceMetrics.resource,
        s = t.resourceMetrics.scopeMetrics.concat(
          (0, HFn.FlatMap)(n, (i) => i.resourceMetrics.scopeMetrics),
        );
      return { resourceMetrics: { resource: o, scopeMetrics: s }, errors: r };
    }
    async shutdown(e) {
      if (this._shutdown) {
        E0a.diag.error("Cannot call shutdown twice.");
        return;
      }
      if (e?.timeoutMillis == null) await this.onShutdown();
      else await (0, HFn.callWithTimeout)(this.onShutdown(), e.timeoutMillis);
      this._shutdown = !0;
    }
    async forceFlush(e) {
      if (this._shutdown) {
        E0a.diag.warn("Cannot forceFlush on already shutdown MetricReader.");
        return;
      }
      if (e?.timeoutMillis == null) {
        await this.onForceFlush();
        return;
      }
      await (0, HFn.callWithTimeout)(this.onForceFlush(), e.timeoutMillis);
    }
  }
  AFn.MetricReader = A0a;
});
var w0a = Q((vFn) => {
  Object.defineProperty(vFn, "__esModule", { value: !0 });
  vFn.PeriodicExportingMetricReader = void 0;
  var Quo = Oi(),
    TFn = Eh(),
    tSp = Juo(),
    T0a = Dne();
  class v0a extends tSp.MetricReader {
    _interval;
    _exporter;
    _exportInterval;
    _exportTimeout;
    constructor(e) {
      super({
        aggregationSelector: e.exporter.selectAggregation?.bind(e.exporter),
        aggregationTemporalitySelector:
          e.exporter.selectAggregationTemporality?.bind(e.exporter),
        metricProducers: e.metricProducers,
      });
      if (e.exportIntervalMillis !== void 0 && e.exportIntervalMillis <= 0)
        throw Error("exportIntervalMillis must be greater than 0");
      if (e.exportTimeoutMillis !== void 0 && e.exportTimeoutMillis <= 0)
        throw Error("exportTimeoutMillis must be greater than 0");
      if (
        e.exportTimeoutMillis !== void 0 &&
        e.exportIntervalMillis !== void 0 &&
        e.exportIntervalMillis < e.exportTimeoutMillis
      )
        throw Error(
          "exportIntervalMillis must be greater than or equal to exportTimeoutMillis",
        );
      ((this._exportInterval = e.exportIntervalMillis ?? 60000),
        (this._exportTimeout = e.exportTimeoutMillis ?? 30000),
        (this._exporter = e.exporter));
    }
    async _runOnce() {
      try {
        await (0, T0a.callWithTimeout)(this._doRun(), this._exportTimeout);
      } catch (e) {
        if (e instanceof T0a.TimeoutError) {
          Quo.diag.error(
            "Export took longer than %s milliseconds and timed out.",
            this._exportTimeout,
          );
          return;
        }
        (0, TFn.globalErrorHandler)(e);
      }
    }
    async _doRun() {
      let { resourceMetrics: e, errors: t } = await this.collect({
        timeoutMillis: this._exportTimeout,
      });
      if (t.length > 0)
        Quo.diag.error(
          "PeriodicExportingMetricReader: metrics collection errors",
          ...t,
        );
      if (e.resource.asyncAttributesPending)
        try {
          await e.resource.waitForAsyncAttributes?.();
        } catch (r) {
          (Quo.diag.debug(
            "Error while resolving async portion of resource: ",
            r,
          ),
            (0, TFn.globalErrorHandler)(r));
        }
      if (e.scopeMetrics.length === 0) return;
      let n = await TFn.internal._export(this._exporter, e);
      if (n.code !== TFn.ExportResultCode.SUCCESS)
        throw Error(
          
