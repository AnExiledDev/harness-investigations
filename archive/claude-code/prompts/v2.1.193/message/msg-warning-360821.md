---
id: msg-warning-360821
name: Warning Message
category: message
subcategory: warning
source_line: 360821
---

,
          ));
      });
      return () => {
        (h(), m());
      };
    }, [m]),
    uLe.jsx(Ykn, {
      bindings: t,
      pendingChordRef: o,
      pendingChord: s,
      setPendingChord: g,
      activeContexts: c.current,
      registerActiveContext: p,
      unregisterActiveContext: f,
      handlerRegistryRef: l,
      preDispatchRef: u,
      keyHandlerRegistry: d,
      children: uLe.jsx(mka, {
        bindings: t,
        pendingChordRef: o,
        setPendingChord: g,
        activeContexts: c.current,
        handlerRegistryRef: l,
        preDispatchRef: u,
        keyHandlerRegistry: d,
        children: e,
      }),
    })
  );
}
function mka(e) {
  let t = vuo.c(28),
    {
      bindings: n,
      pendingChordRef: r,
      setPendingChord: o,
      activeContexts: s,
      handlerRegistryRef: i,
      preDispatchRef: a,
      keyHandlerRegistry: l,
      children: c,
    } = e,
    u;
  if (t[0] === Symbol.for("react.memo_cache_sentinel")) ((u = []), (t[0] = u));
  else u = t[0];
  let d = dI.useRef(u),
    p = dI.useRef(null),
    f = dI.useRef("legacy"),
    m;
  if (t[1] !== a)
    ((m = (P, O, D, M) => {
      for (let U of a.current)
        try {
          if (U(P, O, D) === !0) return (M(), !0);
        } catch (F) {
          ke(F);
        }
      return !1;
    }),
      (t[1] = a),
      (t[2] = m));
  else m = t[2];
  let g = m,
    h;
  if (
    t[3] !== s ||
    t[4] !== n ||
    t[5] !== i ||
    t[6] !== r ||
    t[7] !== g ||
    t[8] !== o
  )
    ((h = (P, O, D, M, U, F) => {
      let $ = F === void 0 ? !1 : F,
        W = i.current,
        G = new Set();
      if (W) for (let X of W.values()) for (let Z of X) G.add(Z.context);
      let z = [...G, ...s, "Global"],
        J = r.current !== null,
        q = zOt(P, z, n, r.current);
      e: switch (q.type) {
        case "chord_started": {
          ((f.current = "legacy"), o(q.pending), U());
          return;
        }
        case "chord_cancelled": {
          (o(null), U());
          return;
        }
        case "unbound": {
          if ((o(null), J)) {
            U();
            return;
          }
          break e;
        }
        case "match": {
          if ((o(null), J)) {
            let X = W?.get(q.action);
            if (X)
              for (let Z of X) {
                (Z.handler(), KWe(q.action), U());
                break;
              }
            return;
          }
          break e;
        }
        case "none":
      }
      if (!W) return;
      if (!$ && g(O, D, M, U)) return;
      let K = new Map();
      for (let X of W.values())
        for (let Z of X) {
          if (!Z.singleKey) continue;
          let te = K.get(Z.context);
          if (te === void 0) {
            let ie = zOt(P, [...s, Z.context, "Global"], n, null);
            ((te = ie.type === "match" ? ie.action : null),
              K.set(Z.context, te));
          }
          if (te === Z.action) {
            if (Z.handler() !== !1) {
              (KWe(te), U());
              return;
            }
          }
        }
    }),
      (t[3] = s),
      (t[4] = n),
      (t[5] = i),
      (t[6] = r),
      (t[7] = g),
      (t[8] = o),
      (t[9] = h));
  else h = t[9];
  let y = h,
    b;
  if (
    t[10] !== n ||
    t[11] !== i ||
    t[12] !== l ||
    t[13] !== y ||
    t[14] !== r ||
    t[15] !== g ||
    t[16] !== o
  )
    ((b = (P, O, D, M, U, F) => {
      let $ = l,
        W = (K, X) => {};
      if ($.swallowAll.size > 0) {
        (W(null, !0), F());
        return;
      }
      if (r.current !== null && f.current === "legacy") {
        (W(null, !1), y(O, D, M, U, F));
        return;
      }
      let G = q_p(P.target),
        z = r.current !== null && f.current === "scopeChain";
      if (G.length === 0 && $.preemptiveScopes.size === 0 && !z) {
        (W(null, !1), y(O, D, M, U, F));
        return;
      }
      let J = qBn(P.target);
      if ($.preemptiveScopes.size > 0 && !z) {
        let K = [...$.preemptiveScopes.keys(), "Global"],
          X = jxn(O, K, n, null);
        if (X.type === "match" && J) {
          if (
            Tuo(J, P, X.action, !1, P.type === "wheel" ? "wheel" : "single")
          ) {
            (W(X.action, !0), KWe(X.action));
            return;
          }
        }
      }
      if (z) {
        let K = jxn(O, d.current, n, r.current);
        if (K.type === "chord_started") {
          ((f.current = "scopeChain"), o(K.pending), F(), W(null, !0));
          return;
        }
        if (K.type === "match") {
          o(null);
          let X = p.current;
          ((p.current = null), (d.current = []));
          let Z = X && J && ite(X, pot(J)) ? X : J;
          if (Z) {
            if (Tuo(Z, P, K.action, !0, "chord")) {
              (W(K.action, !0), KWe(K.action));
              return;
            }
          }
          let te = !1,
            ie = i.current?.get(K.action);
          if (ie)
            for (let ne of ie) {
              (ne.handler(), KWe(K.action), F(), (te = !0));
              break;
            }
          W(K.action, te);
          return;
        }
        ((p.current = null), (d.current = []), W(null, !1), y(O, D, M, U, F));
        return;
      }
      let q = jxn(O, G, n, null);
      switch (q.type) {
        case "chord_started": {
          ((d.current = G),
            (p.current = J ?? null),
            (f.current = "scopeChain"),
            o(q.pending),
            F(),
            W(null, !0));
          return;
        }
        case "match": {
          if (!J) {
            (W(q.action, !1), y(O, D, M, U, F));
            return;
          }
          if (g(D, M, U, F)) {
            (o(null), W(q.action, !0));
            return;
          }
          if (
            Tuo(J, P, q.action, !1, P.type === "wheel" ? "wheel" : "single")
          ) {
            (o(null), W(q.action, !0), KWe(q.action));
            return;
          }
          (W(q.action, !1), y(O, D, M, U, F, !0));
          return;
        }
        case "unbound": {
          if (g(D, M, U, F)) {
            (o(null), W(null, !0));
            return;
          }
          (o(null), W(null, !1));
          return;
        }
        default: {
          (W(null, !1), y(O, D, M, U, F));
          return;
        }
      }
    }),
      (t[10] = n),
      (t[11] = i),
      (t[12] = l),
      (t[13] = y),
      (t[14] = r),
      (t[15] = g),
      (t[16] = o),
      (t[17] = b));
  else b = t[17];
  let _ = b,
    S;
  if (t[18] !== _)
    ((S = (P) => {
      let { input: O, key: D } = i4i(P);
      _(P, P, O, D, P.sequence, () => pka(P));
    }),
      (t[18] = _),
      (t[19] = S));
  else S = t[19];
  let H = S,
    v;
  if (t[20] !== _)
    ((v = (P) => {
      if (V_p(P.target, P.currentTarget)) return;
      let O = {
          name: P.deltaY < 0 ? "wheelup" : "wheeldown",
          key: "",
          ctrl: P.ctrl,
          shift: P.shift,
          meta: P.meta,
          superKey: !1,
        },
        D = {
          upArrow: !1,
          downArrow: !1,
          leftArrow: !1,
          rightArrow: !1,
          pageDown: !1,
          pageUp: !1,
          wheelUp: P.deltaY < 0,
          wheelDown: P.deltaY > 0,
          home: !1,
          end: !1,
          return: !1,
          escape: !1,
          tab: !1,
          backspace: !1,
          delete: !1,
          ctrl: P.ctrl,
          shift: P.shift,
          meta: P.meta,
          super: !1,
        };
      _(P, O, "", D, "", () => pka(P));
    }),
      (t[20] = _),
      (t[21] = v));
  else v = t[21];
  let C = v,
    x = dI.useRef(null),
    I,
    k;
  if (t[22] === Symbol.for("react.memo_cache_sentinel"))
    ((I = () => {
      if (!x.current) return;
      let P = ate(x.current),
        O = () => {
          let D = x.current;
          if (!D || P.activeElement === D) return;
          if (P.activeElement === null) {
            P.focus(D);
            return;
          }
          let M = D.parentNode;
          while (M) {
            if (M === P.activeElement) {
              P.focus(D);
              return;
            }
            M = M.parentNode;
          }
        };
      return (O(), P.subscribe(O));
    }),
      (k = []),
      (t[22] = I),
      (t[23] = k));
  else ((I = t[22]), (k = t[23]));
  dI.useLayoutEffect(I, k);
  let R;
  if (t[24] !== c || t[25] !== H || t[26] !== C)
    ((R = uLe.jsx(dy, {
      ref: x,
      keybindingScope: "Global",
      tabIndex: -1,
      flexDirection: "column",
      flexGrow: 1,
      onKeyDownCapture: H,
      onWheelCapture: C,
      children: c,
    })),
      (t[24] = c),
      (t[25] = H),
      (t[26] = C),
      (t[27] = R));
  else R = t[27];
  return R;
}
function pka(e) {
  (e.preventDefault(), e.stopImmediatePropagation());
}
function W_p(e) {
  return e !== null && "attributes" in e;
}
function qBn(e) {
  return W_p(e) ? e : void 0;
}
function V_p(e, t) {
  let n = qBn(e),
    r = qBn(t);
  while (n && n !== r) {
    if (n._eventHandlers?.onWheel) return !0;
    n = n.parentNode;
  }
  return !1;
}
function q_p(e) {
  let t = [],
    n = qBn(e);
  while (n) {
    let r = n.attributes.keybindingScope;
    if (typeof r === "string" && BBi(r)) t.push(r);
    n = n.parentNode;
  }
  return t;
}
function Tuo(e, t, n, r, o) {
  let s = new Auo(n, { sourceEvent: t, isChordCompletion: r, origin: o });
  return (l9.dispatch(e, s), s.consumed);
}
var vuo,
  dI,
  uLe,
  fka = 1000;
var g8 = E(() => {
  cka();
  Hye();
  e4e();
  fot();
  Xe();
  Ge();
  Tn();
  cKr();
  rj();
  yte();
  Lxe();
  $xn();
  dka();
  ((vuo = L(st(), 1)), (dI = L(et(), 1)), (uLe = L(oe(), 1)));
});
class wuo {
  queue = [];
  waiters = [];
  changed = Pi();
  _revision = 0;
  get length() {
    return this.queue.length;
  }
  get revision() {
    return this._revision;
  }
  send(e) {
    this._revision++;
    let t = this.waiters.findIndex((n) => n.fn(e));
    if (t !== -1) {
      let n = this.waiters.splice(t, 1)[0];
      if (n) {
        (n.resolve(e), this.notify());
        return;
      }
    }
    (this.queue.push(e), this.notify());
  }
  poll(e = () => !0) {
    let t = this.queue.findIndex(e);
    if (t === -1) return;
    return this.queue.splice(t, 1)[0];
  }
  receive(e = () => !0) {
    let t = this.queue.findIndex(e);
    if (t !== -1) {
      let n = this.queue.splice(t, 1)[0];
      if (n) return (this.notify(), Promise.resolve(n));
    }
    return new Promise((n) => {
      this.waiters.push({ fn: e, resolve: n });
    });
  }
  subscribe = this.changed.subscribe;
  notify() {
    this.changed.emit();
  }
}
var hka = E(() => {
  fh();
});
function bka(e) {
  let t = yka.c(3),
    { children: n } = e,
    r;
  if (t[0] === Symbol.for("react.memo_cache_sentinel"))
    ((r = new wuo()), (t[0] = r));
  else r = t[0];
  let o = r,
    s;
  if (t[1] !== n)
    ((s = Eka.jsx(_ka.Provider, { value: o, children: n })),
      (t[1] = n),
      (t[2] = s));
  else s = t[2];
  return s;
}
function Ska() {
  let e = zBn.useContext(_ka);
  if (!e) throw Error("useMailbox must be used within a MailboxProvider");
  return e;
}
var yka, zBn, Eka, _ka;
var Cuo = E(() => {
  hka();
  ((yka = L(st(), 1)),
    (zBn = L(et(), 1)),
    (Eka = L(oe(), 1)),
    (_ka = zBn.createContext(void 0)));
});
function Jut(e) {
  let t = KBn.useRef(e);
  ((t.current = e),
    KBn.useEffect(
      () =>
        HM.subscribe((n) => {
          let r = jo();
          t.current(n, r);
        }),
      [],
    ));
}
var KBn;
var YBn = E(() => {
  Xle();
  gr();
  KBn = L(et(), 1);
});
function iT(e) {
  return (
    typeof e === "object" &&
    e !== null &&
    "type" in e &&
    e.type === "local_bash"
  );
}
function XBn(e) {
  for (let t of Object.values(e)) {
    if (t.status !== "running") continue;
    try {
      if (iT(t)) (t.shellCommand?.kill(), t.shellCommand?.cleanup());
      else if ("abortController" in t) t.abortController?.abort();
      (am(t.id, "stopped", { toolUseId: t.toolUseId, summary: t.description }),
        Ty(t.id));
    } catch (n) {
      ke(n);
    }
  }
}
var Iuo = E(() => {
  Tn();
  KH();
  JH();
});
function JBn(e) {
  return KQ((t, n, r) => {
    if (!r) return;
    (z_p(r, e),
      V("tengu_refusal_fallback_latch_reset", {
        source: $e(n),
        restored_to_explicit_override: r.restoredToExplicitOverride,
        model_scope: $e(N_e(r.fallbackModel)),
      }));
  });
}
function Hka(e) {
  return KQ((t, n, r) => {
    if (r) e();
  });
}
function z_p(e, t) {
  (t((n) => {
    let r = e.overrideValue ?? e.forSessionValue ?? e.appStateModel,
      o = ic() && n.fastMode && !Fm(r);
    return n.mainLoopModel === e.appStateModel &&
      n.mainLoopModelForSession === e.forSessionValue &&
      !o
      ? n
      : {
          ...n,
          mainLoopModel: e.appStateModel,
          mainLoopModelForSession: e.forSessionValue,
          ...(o && { fastMode: !1 }),
        };
  }),
    Yh(e.overrideValue));
}
var QBn = E(() => {
  ut();
  It();
  fE();
  B7();
});
function ZBn(e) {
  if (!/^[A-Za-z]:[\\/]/.test(e)) return [];
  let t = Atn(e);
  if (t != null && jc(t)) return [e, t];
  return [];
}
var xuo = E(() => {
  Mm();
});
function eFn(e, t) {
  let n = Lr();
  if (
    (T(
