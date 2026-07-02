---
id: msg-warning-885780
name: Warning Message
category: message
subcategory: warning
source_line: 885780
---

);
}
function lJm(e) {
  if (typeof e === "object" && e !== null) {
    if ("errno" in e && typeof e.errno === "string") return e.errno;
    if ("code" in e && typeof e.code === "string") return e.code;
  }
  return;
}
var nJm = 30000,
  rJm = 3600000,
  oJm = 13,
  sJm = 90,
  iJm = 365,
  qtu;
var ztu = E(() => {
  ut();
  Ete();
  Gtu();
  qtu = new Set();
});
var Xtu = {};
lt(Xtu, { startGateway: () => gJm, collectBootWarnings: () => Ytu });
function Nae(e, t = 400) {
  return Response.json({ error: e }, { status: t, headers: tln });
}
function cJm() {
  if (typeof Bun > "u")
    throw Error(
      "claude gateway requires the native binary. Install via https://claude.ai/install.sh instead of npm.",
    );
}
function Ktu(e, t) {
  for (let [n, r] of Object.entries(uJm))
    if (!e.headers.has(n)) e.headers.set(n, r);
  if (t && !e.headers.has("Strict-Transport-Security"))
    e.headers.set(
      "Strict-Transport-Security",
      "max-age=31536000; includeSubDomains",
    );
  return e;
}
function mJm(e) {
  let t = e.headers.get(dJm);
  return t && fJm.test(t) ? t : Uhe.randomUUID();
}
async function gJm(e) {
  cJm();
  let t = await Zeu(e);
  Fhe("config.load", {
    path: e,
    sha256: Uhe.createHash("sha256").update(JSON.stringify(t)).digest("hex"),
  });
  let n = WAr(t.listen.trusted_proxies),
    r = WAr(t.access_control.allow_cidrs),
    o = WAr(t.access_control.deny_cidrs),
    s = await Vtu(t.store.postgres_url, {
      auditRetentionDays: t.admin?.audit_retention_days,
      maxConnections: t.store.max_connections,
      username: t.store.username,
      password: t.store.password,
      spendRetentionMonths: t.admin?.spend_retention_months,
      identityRetentionDays: t.admin?.identity_retention_days,
    }).catch((M) => {
      let R = ge(M);
      if (/connect|ECONNREFUSED|ENOTFOUND|ETIMEDOUT/i.test(R))
        throw Error(
          
