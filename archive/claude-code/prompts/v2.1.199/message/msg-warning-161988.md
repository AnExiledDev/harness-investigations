---
id: msg-warning-161988
name: Warning Message
category: message
subcategory: warning
source_line: 161988
---

,
    );
  return t.length > 0 ? t : void 0;
}
function sUt(e) {
  let t = s6(e, "interleaved_thinking");
  if (t !== void 0) return t;
  let n = io(e),
    r = qg(e);
  if (r === "foundry") return !0;
  if (G1(r)) return !n.includes("claude-3-");
  if (n === "claude-haiku-4-5" || n.includes("claude-3-")) return !1;
  return !0;
}
function OGd(e) {
  return (
    e === "claude-fable-5" ||
    e === "claude-mythos-5" ||
    e === "claude-opus-4-0" ||
    e === "claude-opus-4-1" ||
    e === "claude-opus-4-5" ||
    e === "claude-opus-4-6" ||
    e === "claude-opus-4-7" ||
    e === "claude-opus-4-8" ||
    e === "claude-sonnet-4-0" ||
    e === "claude-sonnet-4-5" ||
    e === "claude-sonnet-4-6" ||
    e === "claude-sonnet-5" ||
    e === "claude-haiku-4-5"
  );
}
function NGd(e) {
  let t = io(e),
    n = qg(e);
  if (n === "foundry") return !0;
  if (G1(n)) return !t.includes("claude-3-");
  return wF(t, "context_management") || t === "claude-mythos-5";
}
function cWe(e) {
  let t = io(e),
    n = qg(e);
  if (!G1(n)) return !1;
  if (
    t.includes("claude-3-") ||
    t === "claude-opus-4-0" ||
    t === "claude-sonnet-4-0"
  )
    return !1;
  return !0;
}
function TRn(e) {
  let t = s6(e, "temperature");
  if (t !== void 0) return t;
  let n = io(e);
  if (
    n.includes("claude-3-") ||
    n === "claude-opus-4-0" ||
    n === "claude-opus-4-1" ||
    n === "claude-opus-4-5" ||
    n === "claude-opus-4-6" ||
    n === "claude-sonnet-4-0" ||
    n === "claude-sonnet-4-5" ||
    n === "claude-sonnet-4-6" ||
    n === "claude-haiku-4-5"
  )
    return !0;
  return !1;
}
function elt(e) {
  if (e === "firstParty" || e === "anthropicAws") return !0;
  return at(process.env.CLAUDE_CODE_ENABLE_AUTO_MODE);
}
function vRn() {
  let e = gr();
  return e !== "firstParty" && e !== "anthropicAws" && elt(e);
}
function kXr() {
  return yL() || vRn();
}
function Zbe(e) {
  {
    let t = io(e),
      n = gr();
    if (!elt(n)) return !1;
    if (
      t.includes("claude-3-") ||
      t === "claude-opus-4-0" ||
      t === "claude-opus-4-1" ||
      t === "claude-opus-4-5" ||
      t === "claude-sonnet-4-0" ||
      t === "claude-sonnet-4-5" ||
      t === "claude-haiku-4-5"
    )
      return !1;
    if (
      n !== "firstParty" &&
      n !== "anthropicAws" &&
      (t === "claude-opus-4-6" ||
        t === "claude-sonnet-4-6" ||
        t.includes("haiku"))
    )
      return !1;
    return !0;
  }
  return !1;
}
function HMi() {
  let e = gr();
  if (e === "vertex" || e === "bedrock" || e === "mantle" || e === "gateway")
    return x1t;
  return tqr;
}
function RXr() {
  let e = gr();
  return e === "firstParty" || e === "anthropicAws" || e === "foundry";
}
function lWe() {
  return at(process.env.CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS) || B8("hipaa");
}
function yL() {
  return RXr() && !lWe();
}
function oRe() {
  if (!yL()) return !1;
  if (!gu()) return !1;
  let e = gr();
  return e === "firstParty" || e === "anthropicAws";
}
function tlt(e, t) {
  let n = [...a6(e)];
  if (t?.isAgenticQuery) {
    if (!n.includes(hGe)) n.push(hGe);
  }
  let r = Tb();
  if (!r || r.length === 0) return n;
  let o = r.map(lqr);
  if (!yL())
    o = o.filter((s) => {
      if (TMi.has(s)) return !0;
      return (
        T(
