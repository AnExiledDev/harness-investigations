---
id: msg-warning-413057
name: Warning Message
category: message
subcategory: warning
source_line: 413057
---

),
        lb.DROP_AGGREGATION
      );
    }
    createAggregator(e) {
      return this._resolve(e).createAggregator(e);
    }
  }
  lb.DefaultAggregation = uIo;
  lb.DROP_AGGREGATION = new n6n();
  lb.SUM_AGGREGATION = new j6t();
  lb.LAST_VALUE_AGGREGATION = new r6n();
  lb.HISTOGRAM_AGGREGATION = new o6n();
  lb.EXPONENTIAL_HISTOGRAM_AGGREGATION = new cIo();
  lb.DEFAULT_AGGREGATION = new uIo();
});
var G6t = J((Z6e) => {
  Object.defineProperty(Z6e, "__esModule", { value: !0 });
  Z6e.toAggregation = Z6e.AggregationType = void 0;
  var J6e = QXa(),
    Q6e;
  (function (e) {
    ((e[(e.DEFAULT = 0)] = "DEFAULT"),
      (e[(e.DROP = 1)] = "DROP"),
      (e[(e.SUM = 2)] = "SUM"),
      (e[(e.LAST_VALUE = 3)] = "LAST_VALUE"),
      (e[(e.EXPLICIT_BUCKET_HISTOGRAM = 4)] = "EXPLICIT_BUCKET_HISTOGRAM"),
      (e[(e.EXPONENTIAL_HISTOGRAM = 5)] = "EXPONENTIAL_HISTOGRAM"));
  })((Q6e = Z6e.AggregationType || (Z6e.AggregationType = {})));
  function VJp(e) {
    switch (e.type) {
      case Q6e.DEFAULT:
        return J6e.DEFAULT_AGGREGATION;
      case Q6e.DROP:
        return J6e.DROP_AGGREGATION;
      case Q6e.SUM:
        return J6e.SUM_AGGREGATION;
      case Q6e.LAST_VALUE:
        return J6e.LAST_VALUE_AGGREGATION;
      case Q6e.EXPONENTIAL_HISTOGRAM: {
        let t = e;
        return new J6e.ExponentialHistogramAggregation(
          t.options?.maxSize,
          t.options?.recordMinMax,
        );
      }
      case Q6e.EXPLICIT_BUCKET_HISTOGRAM: {
        let t = e;
        if (t.options == null) return J6e.HISTOGRAM_AGGREGATION;
        else
          return new J6e.ExplicitBucketHistogramAggregation(
            t.options?.boundaries,
            t.options?.recordMinMax,
          );
      }
      default:
        throw Error("Unsupported Aggregation");
    }
  }
  Z6e.toAggregation = VJp;
});
var dIo = J((l_t) => {
  Object.defineProperty(l_t, "__esModule", { value: !0 });
  l_t.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR =
    l_t.DEFAULT_AGGREGATION_SELECTOR = void 0;
  var zJp = q8n(),
    KJp = G6t(),
    YJp = (e) => ({ type: KJp.AggregationType.DEFAULT });
  l_t.DEFAULT_AGGREGATION_SELECTOR = YJp;
  var XJp = (e) => zJp.AggregationTemporality.CUMULATIVE;
  l_t.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR = XJp;
});
var pIo = J((i6n) => {
  Object.defineProperty(i6n, "__esModule", { value: !0 });
  i6n.MetricReader = void 0;
  var ZXa = ea(),
    s6n = Dse(),
    eJa = dIo();
  class tJa {
    _shutdown = !1;
    _metricProducers;
    _sdkMetricProducer;
    _aggregationTemporalitySelector;
    _aggregationSelector;
    _cardinalitySelector;
    constructor(e) {
      ((this._aggregationSelector =
        e?.aggregationSelector ?? eJa.DEFAULT_AGGREGATION_SELECTOR),
        (this._aggregationTemporalitySelector =
          e?.aggregationTemporalitySelector ??
          eJa.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR),
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
        r = t.errors.concat((0, s6n.FlatMap)(n, (i) => i.errors)),
        o = t.resourceMetrics.resource,
        s = t.resourceMetrics.scopeMetrics.concat(
          (0, s6n.FlatMap)(n, (i) => i.resourceMetrics.scopeMetrics),
        );
      return { resourceMetrics: { resource: o, scopeMetrics: s }, errors: r };
    }
    async shutdown(e) {
      if (this._shutdown) {
        ZXa.diag.error("Cannot call shutdown twice.");
        return;
      }
      if (e?.timeoutMillis == null) await this.onShutdown();
      else await (0, s6n.callWithTimeout)(this.onShutdown(), e.timeoutMillis);
      this._shutdown = !0;
    }
    async forceFlush(e) {
      if (this._shutdown) {
        ZXa.diag.warn("Cannot forceFlush on already shutdown MetricReader.");
        return;
      }
      if (e?.timeoutMillis == null) {
        await this.onForceFlush();
        return;
      }
      await (0, s6n.callWithTimeout)(this.onForceFlush(), e.timeoutMillis);
    }
  }
  i6n.MetricReader = tJa;
});
var oJa = J((l6n) => {
  Object.defineProperty(l6n, "__esModule", { value: !0 });
  l6n.PeriodicExportingMetricReader = void 0;
  var fIo = ea(),
    a6n = ey(),
    JJp = pIo(),
    nJa = Dse();
  class rJa extends JJp.MetricReader {
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
        await (0, nJa.callWithTimeout)(this._doRun(), this._exportTimeout);
      } catch (e) {
        if (e instanceof nJa.TimeoutError) {
          fIo.diag.error(
            "Export took longer than %s milliseconds and timed out.",
            this._exportTimeout,
          );
          return;
        }
        (0, a6n.globalErrorHandler)(e);
      }
    }
    async _doRun() {
      let { resourceMetrics: e, errors: t } = await this.collect({
        timeoutMillis: this._exportTimeout,
      });
      if (t.length > 0)
        fIo.diag.error(
          "PeriodicExportingMetricReader: metrics collection errors",
          ...t,
        );
      if (e.resource.asyncAttributesPending)
        try {
          await e.resource.waitForAsyncAttributes?.();
        } catch (r) {
          (fIo.diag.debug(
            "Error while resolving async portion of resource: ",
            r,
          ),
            (0, a6n.globalErrorHandler)(r));
        }
      if (e.scopeMetrics.length === 0) return;
      let n = await a6n.internal._export(this._exporter, e);
      if (n.code !== a6n.ExportResultCode.SUCCESS)
        throw Error(
          
