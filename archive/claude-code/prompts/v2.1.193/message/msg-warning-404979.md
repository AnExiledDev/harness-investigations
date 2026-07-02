---
id: msg-warning-404979
name: Warning Message
category: message
subcategory: warning
source_line: 404979
---

),
        k_.DROP_AGGREGATION
      );
    }
    createAggregator(e) {
      return this._resolve(e).createAggregator(e);
    }
  }
  k_.DefaultAggregation = dgo;
  k_.DROP_AGGREGATION = new B4n();
  k_.SUM_AGGREGATION = new hGt();
  k_.LAST_VALUE_AGGREGATION = new F4n();
  k_.HISTOGRAM_AGGREGATION = new U4n();
  k_.EXPONENTIAL_HISTOGRAM_AGGREGATION = new ugo();
  k_.DEFAULT_AGGREGATION = new dgo();
});
var yGt = Q((j5e) => {
  Object.defineProperty(j5e, "__esModule", { value: !0 });
  j5e.toAggregation = j5e.AggregationType = void 0;
  var F5e = OUa(),
    U5e;
  (function (e) {
    ((e[(e.DEFAULT = 0)] = "DEFAULT"),
      (e[(e.DROP = 1)] = "DROP"),
      (e[(e.SUM = 2)] = "SUM"),
      (e[(e.LAST_VALUE = 3)] = "LAST_VALUE"),
      (e[(e.EXPLICIT_BUCKET_HISTOGRAM = 4)] = "EXPLICIT_BUCKET_HISTOGRAM"),
      (e[(e.EXPONENTIAL_HISTOGRAM = 5)] = "EXPONENTIAL_HISTOGRAM"));
  })((U5e = j5e.AggregationType || (j5e.AggregationType = {})));
  function OMp(e) {
    switch (e.type) {
      case U5e.DEFAULT:
        return F5e.DEFAULT_AGGREGATION;
      case U5e.DROP:
        return F5e.DROP_AGGREGATION;
      case U5e.SUM:
        return F5e.SUM_AGGREGATION;
      case U5e.LAST_VALUE:
        return F5e.LAST_VALUE_AGGREGATION;
      case U5e.EXPONENTIAL_HISTOGRAM: {
        let t = e;
        return new F5e.ExponentialHistogramAggregation(
          t.options?.maxSize,
          t.options?.recordMinMax,
        );
      }
      case U5e.EXPLICIT_BUCKET_HISTOGRAM: {
        let t = e;
        if (t.options == null) return F5e.HISTOGRAM_AGGREGATION;
        else
          return new F5e.ExplicitBucketHistogramAggregation(
            t.options?.boundaries,
            t.options?.recordMinMax,
          );
      }
      default:
        throw Error("Unsupported Aggregation");
    }
  }
  j5e.toAggregation = OMp;
});
var pgo = Q((wpt) => {
  Object.defineProperty(wpt, "__esModule", { value: !0 });
  wpt.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR =
    wpt.DEFAULT_AGGREGATION_SELECTOR = void 0;
  var NMp = I4n(),
    BMp = yGt(),
    FMp = (e) => ({ type: BMp.AggregationType.DEFAULT });
  wpt.DEFAULT_AGGREGATION_SELECTOR = FMp;
  var UMp = (e) => NMp.AggregationTemporality.CUMULATIVE;
  wpt.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR = UMp;
});
var fgo = Q((j4n) => {
  Object.defineProperty(j4n, "__esModule", { value: !0 });
  j4n.MetricReader = void 0;
  var NUa = Oi(),
    BUa = Pue(),
    FUa = pgo();
  class UUa {
    _shutdown = !1;
    _metricProducers;
    _sdkMetricProducer;
    _aggregationTemporalitySelector;
    _aggregationSelector;
    _cardinalitySelector;
    constructor(e) {
      ((this._aggregationSelector =
        e?.aggregationSelector ?? FUa.DEFAULT_AGGREGATION_SELECTOR),
        (this._aggregationTemporalitySelector =
          e?.aggregationTemporalitySelector ??
          FUa.DEFAULT_AGGREGATION_TEMPORALITY_SELECTOR),
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
        NUa.diag.error("Cannot call shutdown twice.");
        return;
      }
      if (e?.timeoutMillis == null) await this.onShutdown();
      else await (0, BUa.callWithTimeout)(this.onShutdown(), e.timeoutMillis);
      this._shutdown = !0;
    }
    async forceFlush(e) {
      if (this._shutdown) {
        NUa.diag.warn("Cannot forceFlush on already shutdown MetricReader.");
        return;
      }
      if (e?.timeoutMillis == null) {
        await this.onForceFlush();
        return;
      }
      await (0, BUa.callWithTimeout)(this.onForceFlush(), e.timeoutMillis);
    }
  }
  j4n.MetricReader = UUa;
});
var WUa = Q((V4n) => {
  Object.defineProperty(V4n, "__esModule", { value: !0 });
  V4n.PeriodicExportingMetricReader = void 0;
  var G4n = Oi(),
    W4n = Kne(),
    jMp = fgo(),
    jUa = Pue(),
    G5e = aSe();
  class GUa extends jMp.MetricReader {
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
            case G5e.InstrumentType.COUNTER:
              return a.counter ?? a.default;
            case G5e.InstrumentType.GAUGE:
              return a.gauge ?? a.default;
            case G5e.InstrumentType.HISTOGRAM:
              return a.histogram ?? a.default;
            case G5e.InstrumentType.OBSERVABLE_COUNTER:
              return a.observableCounter ?? a.default;
            case G5e.InstrumentType.OBSERVABLE_UP_DOWN_COUNTER:
              return a.observableUpDownCounter ?? a.default;
            case G5e.InstrumentType.OBSERVABLE_GAUGE:
              return a.observableGauge ?? a.default;
            case G5e.InstrumentType.UP_DOWN_COUNTER:
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
          (G4n.diag.info(
            
