---
id: msg-warning-175261
name: Warning Message
category: message
subcategory: warning
source_line: 175261
---

,
  };
}
function PB(e) {
  if (e === void 0 || e === null || e === "") return;
  if (typeof e === "number" && eki(e)) return e;
  let t = String(e).toLowerCase(),
    n = nki[t] ?? t;
  if (cje(n)) return n;
  let r = parseInt(t, 10);
  if (!isNaN(r) && eki(r)) return r;
  return;
}
function DIe(e) {
  if (e === "low" || e === "medium" || e === "high" || e === "xhigh") return e;
  return;
}
function iVr(e) {
  let t = Lr().ultracode === !0 || !1;
  if (t) U2();
  return t;
}
function oki(e, t, n, r) {
  return n !== void 0 || r || e !== t ? e : void 0;
}
function uje() {
  let e = process.env.CLAUDE_CODE_EFFORT_LEVEL;
  return e?.toLowerCase() === "unset" || e?.toLowerCase() === "auto"
    ? null
    : PB(e);
}
function dje(e) {
  let t = to(e);
  if (t.includes("opus-4-7")) return !Lt().unpinOpus47LaunchEffort;
  if (t.includes("opus-4-8")) return !Lt().unpinOpus48LaunchEffort;
  if (t.includes("fable-5") || Tq(e)) return !Lt().unpinFable5LaunchEffort;
  return !1;
}
function PIe() {
  let e = Lt();
  return Boolean(
    e.unpinOpus47LaunchEffort &&
    e.unpinOpus48LaunchEffort &&
    e.unpinFable5LaunchEffort,
  );
}
function U2() {
  mn((e) =>
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
function Oee(e, t) {
  if (!gw(e)) return;
  let n = dje(e),
    r = Iwn(e),
    o = uje();
  if (o === null) return n ? r : void 0;
  let s = o ?? (n ? r : void 0) ?? t ?? r;
  if (s === "max" && !lje(e)) return "high";
  if (s === "xhigh" && !LIe(e)) return "high";
  return s;
}
function u$t(e, t, n, r, o) {
  if (!o) return !1;
  let s = Hb();
  if (s === 0 || s === r) return !1;
  if (!gw(n)) return !1;
  if (dje(n)) {
    if (e === void 0 || e === Iwn(n)) return !1;
  } else if (Oee(n, e) === Oee(n, t)) return !1;
  if (fH() && e !== void 0 && DIe(e) === void 0) return !1;
  return !0;
}
function d$t(e) {
  let t = e !== void 0 ? DIe(e) : void 0;
  if (e === void 0 || t !== void 0) {
    let n = co("userSettings", { effortLevel: t });
    if (n.error) return n.error;
  }
  U2();
  return;
}
function aVr(e) {
  if (PB(e) !== void 0) U2();
  return ski({ cli: { effort: e }, env: process.env, settings: Lr() });
}
function JP(e, t) {
  let n = Oee(e, t) ?? "high";
  return tye(n);
}
function IR(e, t) {
  return gw(e) ? JP(e, t) : void 0;
}
function frt(e, t) {
  if (t === void 0) return "";
  let n = Oee(e, t);
  if (n === void 0) return "";
  return 
