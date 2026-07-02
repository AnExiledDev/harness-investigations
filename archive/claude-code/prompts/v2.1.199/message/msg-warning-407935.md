---
id: msg-warning-407935
name: Warning Message
category: message
subcategory: warning
source_line: 407935
---

,
          ));
      });
      return () => {
        (h(), m());
      };
    }, [m]),
    N$e.jsx(mNn, {
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
      children: N$e.jsx(e7a, {
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
function e7a(e) {
  let t = dCo.c(28),
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
  let d = Hx.useRef(u),
    p = Hx.useRef(null),
    f = Hx.useRef("legacy"),
    m;
  if (t[1] !== a)
    ((m = (P, M, R, O) => {
      for (let j of a.current)
        try {
          if (j(P, M, R) === !0) return (O(), !0);
        } catch ($) {
          Re($);
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
    ((h = (P, M, R, O, j, $) => {
      let N = $ === void 0 ? !1 : $,
        W = i.current,
        U = new Set();
      if (W) for (let Q of W.values()) for (let Z of Q) U.add(Z.context);
      let V = [...U, ...s, "Global"],
        z = r.current !== null,
        Y = A4t(P, V, n, r.current);
      e: switch (Y.type) {
        case "chord_started": {
          ((f.current = "legacy"), o(Y.pending), j());
          return;
        }
        case "chord_cancelled": {
          (o(null), j());
          return;
        }
        case "unbound": {
          if ((o(null), z)) {
            j();
            return;
          }
          break e;
        }
        case "match": {
          if ((o(null), z)) {
            let Q = W?.get(Y.action);
            if (Q)
              for (let Z of Q) {
                (Z.handler(), R6e(Y.action), j());
                break;
              }
            return;
          }
          break e;
        }
        case "none":
      }
      if (!W) return;
      if (!N && g(M, R, O, j)) return;
      let X = new Map();
      for (let Q of W.values())
        for (let Z of Q) {
          if (!Z.singleKey) continue;
          let re = X.get(Z.context);
          if (re === void 0) {
            let se = A4t(P, [...s, Z.context, "Global"], n, null);
            ((re = se.type === "match" ? se.action : null),
              X.set(Z.context, re));
          }
          if (re === Z.action) {
            if (Z.handler() !== !1) {
              (R6e(re), j());
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
    _;
  if (
    t[10] !== n ||
    t[11] !== i ||
    t[12] !== l ||
    t[13] !== y ||
    t[14] !== r ||
    t[15] !== g ||
    t[16] !== o
  )
    ((_ = (P, M, R, O, j, $) => {
      let N = l,
        W = (X, Q) => {};
      if (N.swallowAll.size > 0) {
        (W(null, !0), $());
        return;
      }
      if (r.current !== null && f.current === "legacy") {
        (W(null, !1), y(M, R, O, j, $));
        return;
      }
      let U = eXp(P.target),
        V = r.current !== null && f.current === "scopeChain";
      if (U.length === 0 && N.preemptiveScopes.size === 0 && !V) {
        (W(null, !1), y(M, R, O, j, $));
        return;
      }
      let z = l8n(P.target);
      if (N.preemptiveScopes.size > 0 && !V) {
        let X = [...N.preemptiveScopes.keys(), "Global"],
          Q = s1n(M, X, n, null);
        if (Q.type === "match" && z) {
          if (
            uCo(z, P, Q.action, !1, P.type === "wheel" ? "wheel" : "single")
          ) {
            (W(Q.action, !0), R6e(Q.action));
            return;
          }
        }
      }
      if (V) {
        let X = s1n(M, d.current, n, r.current);
        if (X.type === "chord_started") {
          ((f.current = "scopeChain"), o(X.pending), $(), W(null, !0));
          return;
        }
        if (X.type === "match") {
          o(null);
          let Q = p.current;
          ((p.current = null), (d.current = []));
          let Z = Q && z && Yre(Q, rut(z)) ? Q : z;
          if (Z) {
            if (uCo(Z, P, X.action, !0, "chord")) {
              (W(X.action, !0), R6e(X.action));
              return;
            }
          }
          let re = !1,
            se = i.current?.get(X.action);
          if (se)
            for (let ee of se) {
              (ee.handler(), R6e(X.action), $(), (re = !0));
              break;
            }
          W(X.action, re);
          return;
        }
        ((p.current = null), (d.current = []), W(null, !1), y(M, R, O, j, $));
        return;
      }
      let Y = s1n(M, U, n, null);
      switch (Y.type) {
        case "chord_started": {
          ((d.current = U),
            (p.current = z ?? null),
            (f.current = "scopeChain"),
            o(Y.pending),
            $(),
            W(null, !0));
          return;
        }
        case "match": {
          if (!z) {
            (W(Y.action, !1), y(M, R, O, j, $));
            return;
          }
          if (g(R, O, j, $)) {
            (o(null), W(Y.action, !0));
            return;
          }
          if (
            uCo(z, P, Y.action, !1, P.type === "wheel" ? "wheel" : "single")
          ) {
            (o(null), W(Y.action, !0), R6e(Y.action));
            return;
          }
          (W(Y.action, !1), y(M, R, O, j, $, !0));
          return;
        }
        case "unbound": {
          if (g(R, O, j, $)) {
            (o(null), W(null, !0));
            return;
          }
          (o(null), W(null, !1));
          return;
        }
        default: {
          (W(null, !1), y(M, R, O, j, $));
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
      (t[17] = _));
  else _ = t[17];
  let b = _,
    S;
  if (t[18] !== b)
    ((S = (P) => {
      let { input: M, key: R } = Lna(P);
      b(P, P, M, R, P.sequence, () => QYa(P));
    }),
      (t[18] = b),
      (t[19] = S));
  else S = t[19];
  let H = S,
    v;
  if (t[20] !== b)
    ((v = (P) => {
      if (Z7p(P.target, P.currentTarget)) return;
      let M = {
          name: P.deltaY < 0 ? "wheelup" : "wheeldown",
          key: "",
          ctrl: P.ctrl,
          shift: P.shift,
          meta: P.meta,
          superKey: !1,
        },
        R = {
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
      b(P, M, "", R, "", () => QYa(P));
    }),
      (t[20] = b),
      (t[21] = v));
  else v = t[21];
  let I = v,
    x = Hx.useRef(null),
    C,
    k;
  if (t[22] === Symbol.for("react.memo_cache_sentinel"))
    ((C = () => {
      if (!x.current) return;
      let P = Xre(x.current),
        M = () => {
          let R = x.current;
          if (!R || P.activeElement === R) return;
          if (P.activeElement === null) {
            P.focus(R);
            return;
          }
          let O = R.parentNode;
          while (O) {
            if (O === P.activeElement) {
              P.focus(R);
              return;
            }
            O = O.parentNode;
          }
        };
      return (M(), P.subscribe(M));
    }),
      (k = []),
      (t[22] = C),
      (t[23] = k));
  else ((C = t[22]), (k = t[23]));
  Hx.useLayoutEffect(C, k);
  let L;
  if (t[24] !== c || t[25] !== H || t[26] !== I)
    ((L = N$e.jsx(Oy, {
      ref: x,
      keybindingScope: "Global",
      tabIndex: -1,
      flexDirection: "column",
      flexGrow: 1,
      onKeyDownCapture: H,
      onWheelCapture: I,
      children: c,
    })),
      (t[24] = c),
      (t[25] = H),
      (t[26] = I),
      (t[27] = L));
  else L = t[27];
  return L;
}
function QYa(e) {
  (e.preventDefault(), e.stopImmediatePropagation());
}
function Q7p(e) {
  return e !== null && "attributes" in e;
}
function l8n(e) {
  return Q7p(e) ? e : void 0;
}
function Z7p(e, t) {
  let n = l8n(e),
    r = l8n(t);
  while (n && n !== r) {
    if (n._eventHandlers?.onWheel) return !0;
    n = n.parentNode;
  }
  return !1;
}
function eXp(e) {
  let t = [],
    n = l8n(e);
  while (n) {
    let r = n.attributes.keybindingScope;
    if (typeof r === "string" && pQi(r)) t.push(r);
    n = n.parentNode;
  }
  return t;
}
function uCo(e, t, n, r, o) {
  let s = new cCo(n, { sourceEvent: t, isChordCompletion: r, origin: o });
  return (I6.dispatch(e, s), s.consumed);
}
var dCo,
  Hx,
  N$e,
  ZYa = 1000;
var Gq = E(() => {
  YYa();
  KSe();
  q5e();
  out();
  nt();
  We();
  Cn();
  Rio();
  TU();
  ioe();
  RLe();
  QOn();
  JYa();
  ((dCo = D(gt(), 1)), (Hx = D(st(), 1)), (N$e = D(ae(), 1)));
});
class fCo {
  queue = [];
  waiters = [];
  changed = hi();
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
var t7a = E(() => {
  Wm();
});
function o7a(e) {
  let t = n7a.c(3),
    { children: n } = e,
    r;
  if (t[0] === Symbol.for("react.memo_cache_sentinel"))
    ((r = new fCo()), (t[0] = r));
  else r = t[0];
  let o = r,
    s;
  if (t[1] !== n)
    ((s = i7a.jsx(r7a.Provider, { value: o, children: n })),
      (t[1] = n),
      (t[2] = s));
  else s = t[2];
  return s;
}
function s7a() {
  let e = c8n.useContext(r7a);
  if (!e) throw Error("useMailbox must be used within a MailboxProvider");
  return e;
}
var n7a, c8n, i7a, r7a;
var mCo = E(() => {
  t7a();
  ((n7a = D(gt(), 1)),
    (c8n = D(st(), 1)),
    (i7a = D(ae(), 1)),
    (r7a = c8n.createContext(void 0)));
});
function Byt(e) {
  let t = u8n.useRef(e);
  ((t.current = e),
    u8n.useEffect(
      () =>
        xP.subscribe((n) => {
          let r = ts();
          t.current(n, r);
        }),
      [],
    ));
}
var u8n;
var d8n = E(() => {
  Wde();
  fr();
  u8n = D(st(), 1);
});
function tXp(e) {
  return L6e.join(a7a(), 
