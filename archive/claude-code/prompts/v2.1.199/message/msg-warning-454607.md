---
id: msg-warning-454607
name: Warning Message
category: message
subcategory: warning
source_line: 454607
---

),
        cb.DROP_AGGREGATION
      );
    }
    createAggregator(e) {
      return this._resolve(e).createAggregator(e);
    }
  }
  cb.DefaultAggregation = wRo;
  cb.DROP_AGGREGATION = new A7n();
  cb.SUM_AGGREGATION = new HKt();
  cb.LAST_VALUE_AGGREGATION = new H7n();
  cb.HISTOGRAM_AGGREGATION = new T7n();
  cb.EXPONENTIAL_HISTOGRAM_AGGREGATION = new vRo();
  cb.DEFAULT_AGGREGATION = new wRo();
});
var TKt = J((Nze) => {
  Object.defineProperty(Nze, "__esModule", { value: !0 });
  Nze.toAggregation = Nze.AggregationType = void 0;
  var $ze = gcl(),
    Oze;
  (function (e) {
    ((e[(e.DEFAULT = 0)] = "DEFAULT"),
      (e[(e.DROP = 1)] = "DROP"),
      (e[(e.SUM = 2)] = "SUM"),
      (e[(e.LAST_VALUE = 3)] = "LAST_VALUE"),
      (e[(e.EXPLICIT_BUCKET_HISTOGRAM = 4)] = "EXPLICIT_BUCKET_HISTOGRAM"),
      (e[(e.EXPONENTIAL_HISTOGRAM = 5)] = "EXPONENTIAL_HISTOGRAM"));
  })((Oze = Nze.AggregationType || (Nze.AggregationType = {})));
  function Dmf(e) {
    switch (e.type) {
      case Oze.DEFAULT:
        return $ze.DEFAULT_AGGREGATION;
      case Oze.DROP:
        return $ze.DROP_AGGREGATION;
      case Oze.SUM:
        return $ze.SUM_AGGREGATION;
      case Oze.LAST_VALUE:
        return $ze.LAST_VALUE_AGGREGATION;
      case Oze.EXPONENTIAL_HISTOGRAM: {
        let t = e;
        return new $ze.ExponentialHistogramAggregation(
          t.options?.maxSize,
          t.options?.recordMinMax,
        );
      }
      case Oze.EXPLICIT_BUCKET_HISTOGRAM: {
        let t = e;
        if (t.options == null) return $ze.HISTOGRAM_AGGREGATION;
        else
          return new $ze.ExplicitBucketHistogramAggregation(
            t.options?.boundaries,
            t.options?.recordMinMax,
          );
      }
      default:
        throw Error("Unsupported Aggregation");
    }
  }
  Nze.toAggregation = Dmf;
});
var CRo = J((Tbt) => {
  Object.defineProperty(Tbt, "__esModule", { value: !0 });
  Tbt.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR =
    Tbt.DEFAULT_AGGREGATION_SELECTOR = void 0;
  var Pmf = d7n(),
    Mmf = TKt(),
    $mf = (e) => ({ type: Mmf.AggregationType.DEFAULT });
  Tbt.DEFAULT_AGGREGATION_SELECTOR = $mf;
  var Omf = (e) => Pmf.AggregationTemporality.CUMULATIVE;
  Tbt.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR = Omf;
});
var IRo = J((v7n) => {
  Object.defineProperty(v7n, "__esModule", { value: !0 });
  v7n.MetricReader = void 0;
  var hcl = ea(),
    ycl = Jfe(),
    _cl = CRo();
  class bcl {
    _shutdown = !1;
    _metricProducers;
    _sdkMetricProducer;
    _aggregationTemporalitySelector;
    _aggregationSelector;
    _cardinalitySelector;
    constructor(e) {
      ((this._aggregationSelector =
        e?.aggregationSelector ?? _cl.DEFAULT_AGGREGATION_SELECTOR),
        (this._aggregationTemporalitySelector =
          e?.aggregationTemporalitySelector ??
          _cl.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR),
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
        r = t.errors.concat(n.flatMap((i) => i.errors)),
        o = t.resourceMetrics.resource,
        s = t.resourceMetrics.scopeMetrics.concat(
          n.flatMap((i) => i.resourceMetrics.scopeMetrics),
        );
      return { resourceMetrics: { resource: o, scopeMetrics: s }, errors: r };
    }
    async shutdown(e) {
      if (this._shutdown) {
        hcl.diag.error("Cannot call shutdown twice.");
        return;
      }
      if (e?.timeoutMillis == null) await this.onShutdown();
      else await (0, ycl.callWithTimeout)(this.onShutdown(), e.timeoutMillis);
      this._shutdown = !0;
    }
    async forceFlush(e) {
      if (this._shutdown) {
        hcl.diag.warn("Cannot forceFlush on already shutdown MetricReader.");
        return;
      }
      if (e?.timeoutMillis == null) {
        await this.onForceFlush();
        return;
      }
      await (0, ycl.callWithTimeout)(this.onForceFlush(), e.timeoutMillis);
    }
  }
  v7n.MetricReader = bcl;
});
var Acl = J((I7n) => {
  Object.defineProperty(I7n, "__esModule", { value: !0 });
  I7n.PeriodicExportingMetricReader = void 0;
  var w7n = ea(),
    C7n = Kse(),
    Nmf = IRo(),
    Scl = Jfe(),
    Bze = XHe();
  class Ecl extends Nmf.MetricReader {
    _interval;
    _exporter;
    _exportInterval;
    _exportTimeout;
    constructor(e) {
      let {
          exporter: t,
          exportIntervalMillis: n = 60000,
          metricProducers: r,
          cardinalityLimits: o,
        } = e,
        { exportTimeoutMillis: s = 30000 } = e;
      super({
        aggregationSelector: t.selectAggregation?.bind(t),
        aggregationTemporalitySelector: t.selectAggregationTemporality?.bind(t),
        metricProducers: r,
        cardinalitySelector: (i) => {
          let a = { default: 2000, ...o };
          switch (i) {
            case Bze.InstrumentType.COUNTER:
              return a.counter ?? a.default;
            case Bze.InstrumentType.GAUGE:
              return a.gauge ?? a.default;
            case Bze.InstrumentType.HISTOGRAM:
              return a.histogram ?? a.default;
            case Bze.InstrumentType.OBSERVABLE_COUNTER:
              return a.observableCounter ?? a.default;
            case Bze.InstrumentType.OBSERVABLE_UP_DOWN_COUNTER:
              return a.observableUpDownCounter ?? a.default;
            case Bze.InstrumentType.OBSERVABLE_GAUGE:
              return a.observableGauge ?? a.default;
            case Bze.InstrumentType.UP_DOWN_COUNTER:
              return a.upDownCounter ?? a.default;
            default:
              return a.default;
          }
        },
      });
      if (n <= 0) throw Error("exportIntervalMillis must be greater than 0");
      if (s <= 0) throw Error("exportTimeoutMillis must be greater than 0");
      if (n < s)
        if ("exportIntervalMillis" in e && "exportTimeoutMillis" in e)
          throw Error(
            "exportIntervalMillis must be greater than or equal to exportTimeoutMillis",
          );
        else
          (w7n.diag.info(
            
