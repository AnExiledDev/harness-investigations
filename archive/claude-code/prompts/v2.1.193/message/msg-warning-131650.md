---
id: msg-warning-131650
name: Warning Message
category: message
subcategory: warning
source_line: 131650
---

);
  }
}
var BZu = "tracingPolicy";
var qoi = E(() => {
  WBr();
  NBr();
  Qbn();
  wCe();
  dSn();
  iSn();
});
function pSn(e) {
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
function zoi() {
  return {
    name: WZu,
    sendRequest: async (e, t) => {
      if (!e.abortSignal) return t(e);
      let { abortSignal: n, cleanup: r } = pSn(e.abortSignal);
      e.abortSignal = n;
      try {
        return await t(e);
      } finally {
        r === null || r === void 0 || r();
      }
    },
  };
}
var WZu = "wrapAbortSignalLikePolicy";
var Koi = () => {};
function VBr(e) {
  var t;
  let n = mLt();
  if (_Lt) {
    if (e.agent) n.addPolicy(Moi(e.agent));
    if (e.tlsOptions) n.addPolicy(Ooi(e.tlsOptions));
    (n.addPolicy(Loi(e.proxyOptions)), n.addPolicy(woi()));
  }
  if (
    (n.addPolicy(zoi()),
    n.addPolicy(koi(), { beforePolicies: [jBr] }),
    n.addPolicy(foi(e.userAgentOptions)),
    n.addPolicy(
      Poi(
        (t = e.telemetryOptions) === null || t === void 0
          ? void 0
          : t.clientRequestIdHeaderName,
      ),
    ),
    n.addPolicy(Toi(), { afterPhase: "Deserialize" }),
    n.addPolicy(Ioi(e.retryOptions), { phase: "Retry" }),
    n.addPolicy(
      Voi(
        Object.assign(Object.assign({}, e.userAgentOptions), e.loggingOptions),
      ),
      { afterPhase: "Retry" },
    ),
    _Lt)
  )
    n.addPolicy(soi(e.redirectOptions), { afterPhase: "Retry" });
  return (n.addPolicy(roi(e.loggingOptions), { afterPhase: "Sign" }), n);
}
var Yoi = E(() => {
  ooi();
  pBr();
  ioi();
  moi();
  voi();
  Coi();
  xoi();
  Roi();
  wCe();
  Doi();
  $oi();
  Noi();
  qoi();
  Koi();
});
function qBr() {
  let e = dBr();
  return {
    async sendRequest(t) {
      let { abortSignal: n, cleanup: r } = t.abortSignal
        ? pSn(t.abortSignal)
        : {};
      try {
        return ((t.abortSignal = n), await e.sendRequest(t));
      } finally {
        r === null || r === void 0 || r();
      }
    },
  };
}
var Xoi = E(() => {
  Ket();
});
function ehe(e) {
  return Xie(e);
}
var Joi = E(() => {
  Ket();
});
function xq(e) {
  return oBr(e);
}
var Qoi = E(() => {
  Ket();
});
function zBr(e, t = { maxRetries: uoi }) {
  return yLt(e, Object.assign({ logger: VZu }, t));
}
var VZu;
var Zoi = E(() => {
  sUe();
  lee();
  VZu = TCe("core-rest-pipeline retryPolicy");
});
async function zZu(e, t, n) {
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
  while (o === null) (await FBr(t), (o = await r()));
  return o;
}
function esi(e, t) {
  let n = null,
    r = null,
    o,
    s = Object.assign(Object.assign({}, qZu), t),
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
      n = zZu(
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
var qZu;
var tsi = E(() => {
  wCe();
  qZu = {
    forcedRefreshWindowInMs: 1000,
    retryIntervalInMs: 3000,
    refreshWindowInMs: 120000,
  };
});
async function fSn(e, t) {
  try {
    return [await t(e), void 0];
  } catch (n) {
    if (HLt(n) && n.response) return [n.response, n];
    else throw n;
  }
}
async function KZu(e) {
  let { scopes: t, getAccessToken: n, request: r } = e,
    o = {
      abortSignal: r.abortSignal,
      tracingOptions: r.tracingOptions,
      enableCae: !0,
    },
    s = await n(t, o);
  if (s) e.request.headers.set("Authorization", 
