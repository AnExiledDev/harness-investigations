---
id: msg-warning-178076
name: Warning Message
category: message
subcategory: warning
source_line: 178076
---

,
  };
}
function sU(e) {
  if (e === void 0 || e === null || e === "") return;
  if (typeof e === "number" && S5i(e)) return e;
  let t = String(e).toLowerCase(),
    n = T5i[t] ?? t;
  if (Due(n)) return n;
  let r = parseInt(t, 10);
  if (!isNaN(r) && S5i(r)) return r;
  return;
}
function DRe(e) {
  if (e === "low" || e === "medium" || e === "high" || e === "xhigh") return e;
  return;
}
function Seo() {
  let e = xr().ultracode === !0;
  if (e) iU();
  return e;
}
function w5i(e, t, n, r) {
  return n !== void 0 || r || e !== t ? e : void 0;
}
function e5e() {
  let e = process.env.CLAUDE_CODE_EFFORT_LEVEL;
  return e?.toLowerCase() === "unset" || e?.toLowerCase() === "auto"
    ? null
    : sU(e);
}
function t5e(e) {
  let t = io(e);
  if (t.includes("opus-4-7")) return !Dt().unpinOpus47LaunchEffort;
  if (t.includes("opus-4-8")) return !Dt().unpinOpus48LaunchEffort;
  if (t.includes("fable-5") || GW(e)) return !Dt().unpinFable5LaunchEffort;
  return !1;
}
function PRe() {
  let e = Dt();
  return Boolean(
    e.unpinOpus47LaunchEffort &&
    e.unpinOpus48LaunchEffort &&
    e.unpinFable5LaunchEffort,
  );
}
function iU() {
  yn((e) =>
    e.unpinOpus47LaunchEffort &&
    e.unpinOpus48LaunchEffort &&
    e.unpinFable5LaunchEffort
      ? e
      : {
          ...e,
          unpinOpus47LaunchEffort: !0,
          unpinOpus48LaunchEffort: !0,
          unpinFable5LaunchEffort: !0,
        },
  );
}
function sJ(e, t) {
  if (!SC(e)) return;
  let n = t5e(e),
    r = M2t(e),
    o = e5e();
  if (o === null && !n) return;
  let i = o ?? (n ? r : void 0) ?? t ?? r;
  if (typeof i === "string" && Due(i)) i = LRe(i, e);
  if (i === "max" && !RRe(e)) i = "high";
  if (i === "xhigh" && !Cre(e)) i = "high";
  return i;
}
function D2t(e, t, n, r, o) {
  if (!o) return !1;
  let s = cS();
  if (s === 0 || s === r) return !1;
  if (!SC(n)) return !1;
  if (t5e(n)) {
    if (e === void 0 || e === M2t(n)) return !1;
  } else if (sJ(n, e) === sJ(n, t)) return !1;
  if (
    f_() &&
    e !== void 0 &&
    DRe(typeof e === "string" ? LRe(e, n) : e) === void 0
  )
    return !1;
  return !0;
}
async function P2t(e) {
  let t = e !== void 0 ? DRe(e) : void 0;
  if ((e === void 0 || t !== void 0) && !ql()) {
    let n = await Qo("userSettings", { effortLevel: t });
    if (n.error) return n.error;
  }
  iU();
  return;
}
function YPn(e) {
  if (sU(e) !== void 0) iU();
  return C5i({ cli: { effort: e }, env: process.env, settings: xr() });
}
function A$(e, t) {
  let n = sJ(e, t) ?? "high";
  return vSe(n);
}
function TL(e, t) {
  return SC(e) ? A$(e, t) : void 0;
}
function oct(e, t) {
  if (t === void 0) return "";
  let n = sJ(e, t);
  if (n === void 0) return "";
  return 
