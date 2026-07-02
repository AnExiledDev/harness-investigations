---
id: msg-warning-159074
name: Warning Message
category: message
subcategory: warning
source_line: 159074
---

,
    );
  return t.length > 0 ? t : void 0;
}
function BPt(e) {
  let t = Uq(e, "interleaved_thinking");
  if (t !== void 0) return t;
  let n = to(e),
    r = Uy(e);
  if (r === "foundry") return !0;
  if (bO(r)) return !n.includes("claude-3-");
  if (n === "claude-haiku-4-5" || n.includes("claude-3-")) return !1;
  return !0;
}
function imd(e) {
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
    e === "claude-haiku-4-5"
  );
}
function amd(e) {
  let t = to(e),
    n = Uy(e);
  if (n === "foundry") return !0;
  if (bO(n)) return !t.includes("claude-3-");
  return (
    t === "claude-fable-5" ||
    t === "claude-mythos-5" ||
    t === "claude-opus-4-0" ||
    t === "claude-opus-4-1" ||
    t === "claude-opus-4-5" ||
    t === "claude-opus-4-6" ||
    t === "claude-opus-4-7" ||
    t === "claude-opus-4-8" ||
    t === "claude-sonnet-4-0" ||
    t === "claude-sonnet-4-5" ||
    t === "claude-sonnet-4-6" ||
    t === "claude-haiku-4-5"
  );
}
function T2e(e) {
  let t = to(e),
    n = Uy(e);
  if (!bO(n)) return !1;
  if (
    t.includes("claude-3-") ||
    t === "claude-opus-4-0" ||
    t === "claude-sonnet-4-0"
  )
    return !1;
  return !0;
}
function vAn(e) {
  let t = Uq(e, "temperature");
  if (t !== void 0) return t;
  let n = to(e);
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
function ont(e) {
  if (e === "firstParty" || e === "anthropicAws") return !0;
  return at(process.env.CLAUDE_CODE_ENABLE_AUTO_MODE);
}
function wAn() {
  let e = _r();
  return e !== "firstParty" && e !== "anthropicAws" && ont(e);
}
function H3r() {
  return zP() || wAn();
}
function Lhe(e) {
  {
    let t = to(e),
      n = _r();
    if (!ont(n)) return !1;
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
function fhi() {
  let e = _r();
  if (e === "vertex" || e === "bedrock" || e === "mantle" || e === "gateway")
    return _Rt;
  return uOr;
}
function A3r() {
  let e = _r();
  return e === "firstParty" || e === "anthropicAws" || e === "foundry";
}
function A2e() {
  return at(process.env.CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS) || Eq("hipaa");
}
function zP() {
  return A3r() && !A2e();
}
function cIe() {
  if (!zP()) return !1;
  if (!_u()) return !1;
  let e = _r();
  return e === "firstParty" || e === "anthropicAws";
}
function snt(e, t) {
  let n = [...Gq(e)];
  if (t?.isAgenticQuery) {
    if (!n.includes(DFe)) n.push(DFe);
  }
  let r = mS();
  if (!r || r.length === 0) return n;
  let o = r.map(yOr);
  if (!zP())
    o = o.filter((s) => {
      if (mhi.has(s)) return !0;
      return (
        T(
