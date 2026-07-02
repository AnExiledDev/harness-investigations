---
id: msg-warning-134510
name: Warning Message
category: message
subcategory: warning
source_line: 134510
---

);
  }
}
var fLd = "tracingPolicy";
var svi = E(() => {
  z8r();
  U8r();
  nxn();
  S0e();
  gxn();
  uxn();
});
function hxn(e) {
  if (e instanceof AbortSignal) return { abortSignal: e };
  if (e.aborted) return { abortSignal: AbortSignal.abort(e.reason) };
  let t = new AbortController(),
    n = !0;
  function r() {
    if (n) (e.removeEventListener("abort", o), (n = !1));
  }
  function o() {
    (t.abort(e.reason), r());
  }
  return (
    e.addEventListener("abort", o),
    { abortSignal: t.signal, cleanup: r }
  );
}
function ivi() {
  return {
    name: _Ld,
    sendRequest: async (e, t) => {
      if (!e.abortSignal) return t(e);
      let { abortSignal: n, cleanup: r } = hxn(e.abortSignal);
      e.abortSignal = n;
      try {
        return await t(e);
      } finally {
        r === null || r === void 0 || r();
      }
    },
  };
}
var _Ld = "wrapAbortSignalLikePolicy";
var avi = () => {};
function K8r(e) {
  var t;
  let n = kNt();
  if (PNt) {
    if (e.agent) n.addPolicy(KTi(e.agent));
    if (e.tlsOptions) n.addPolicy(XTi(e.tlsOptions));
    (n.addPolicy(qTi(e.proxyOptions)), n.addPolicy(BTi()));
  }
  if (
    (n.addPolicy(ivi()),
    n.addPolicy(GTi(), { beforePolicies: [q8r] }),
    n.addPolicy(wTi(e.userAgentOptions)),
    n.addPolicy(
      zTi(
        (t = e.telemetryOptions) === null || t === void 0
          ? void 0
          : t.clientRequestIdHeaderName,
      ),
    ),
    n.addPolicy(OTi(), { afterPhase: "Deserialize" }),
    n.addPolicy(UTi(e.retryOptions), { phase: "Retry" }),
    n.addPolicy(
      ovi(
        Object.assign(Object.assign({}, e.userAgentOptions), e.loggingOptions),
      ),
      { afterPhase: "Retry" },
    ),
    PNt)
  )
    n.addPolicy(_Ti(e.redirectOptions), { afterPhase: "Retry" });
  return (n.addPolicy(hTi(e.loggingOptions), { afterPhase: "Sign" }), n);
}
var lvi = E(() => {
  yTi();
  g8r();
  bTi();
  CTi();
  NTi();
  FTi();
  jTi();
  WTi();
  S0e();
  VTi();
  YTi();
  JTi();
  svi();
  avi();
});
function Y8r() {
  let e = m8r();
  return {
    async sendRequest(t) {
      let { abortSignal: n, cleanup: r } = t.abortSignal
        ? hxn(t.abortSignal)
        : {};
      try {
        return ((t.abortSignal = n), await e.sendRequest(t));
      } finally {
        r === null || r === void 0 || r();
      }
    },
  };
}
var cvi = E(() => {
  Git();
});
function Sbe(e) {
  return Wce(e);
}
var uvi = E(() => {
  Git();
});
function V8(e) {
  return a8r(e);
}
var dvi = E(() => {
  Git();
});
function X8r(e, t = { maxRetries: HTi }) {
  return DNt(e, Object.assign({ logger: bLd }, t));
}
var bLd;
var pvi = E(() => {
  qGe();
  ere();
  bLd = _0e("core-rest-pipeline retryPolicy");
});
async function ELd(e, t, n) {
  async function r() {
    if (Date.now() < n)
      try {
        return await e();
      } catch (s) {
        return null;
      }
    else {
      let s = await e();
      if (s === null) throw Error("Failed to refresh access token.");
      return s;
    }
  }
  let o = await r();
  while (o === null) (await G8r(t), (o = await r()));
  return o;
}
function fvi(e, t) {
  let n = null,
    r = null,
    o,
    s = Object.assign(Object.assign({}, SLd), t),
    i = {
      get isRefreshing() {
        return n !== null;
      },
      get shouldRefresh() {
        var l;
        if (i.isRefreshing) return !1;
        if (
          (r === null || r === void 0 ? void 0 : r.refreshAfterTimestamp) &&
          r.refreshAfterTimestamp < Date.now()
        )
          return !0;
        return (
          ((l = r === null || r === void 0 ? void 0 : r.expiresOnTimestamp) !==
            null && l !== void 0
            ? l
            : 0) -
            s.refreshWindowInMs <
          Date.now()
        );
      },
      get mustRefresh() {
        return (
          r === null ||
          r.expiresOnTimestamp - s.forcedRefreshWindowInMs < Date.now()
        );
      },
    };
  function a(l, c) {
    var u;
    if (!i.isRefreshing)
      n = ELd(
        () => e.getToken(l, c),
        s.retryIntervalInMs,
        (u = r === null || r === void 0 ? void 0 : r.expiresOnTimestamp) !==
          null && u !== void 0
          ? u
          : Date.now(),
      )
        .then((p) => ((n = null), (r = p), (o = c.tenantId), r))
        .catch((p) => {
          throw ((n = null), (r = null), (o = void 0), p);
        });
    return n;
  }
  return async (l, c) => {
    let u = Boolean(c.claims),
      d = o !== c.tenantId;
    if (u) r = null;
    if (d || u || i.mustRefresh) return a(l, c);
    if (i.shouldRefresh) a(l, c);
    return r;
  };
}
var SLd;
var mvi = E(() => {
  S0e();
  SLd = {
    forcedRefreshWindowInMs: 1000,
    retryIntervalInMs: 3000,
    refreshWindowInMs: 120000,
  };
});
async function yxn(e, t) {
  try {
    return [await t(e), void 0];
  } catch (n) {
    if (NNt(n) && n.response) return [n.response, n];
    else throw n;
  }
}
async function ALd(e) {
  let { scopes: t, getAccessToken: n, request: r } = e,
    o = {
      abortSignal: r.abortSignal,
      tracingOptions: r.tracingOptions,
      enableCae: !0,
    },
    s = await n(t, o);
  if (s) e.request.headers.set("Authorization", 
