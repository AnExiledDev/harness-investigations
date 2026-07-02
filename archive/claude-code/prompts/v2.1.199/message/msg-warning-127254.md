---
id: msg-warning-127254
name: Warning Message
category: message
subcategory: warning
source_line: 127254
---

,
    );
}
var Kxd = 300000,
  yVr;
var Tit = E(() => {
  Jh();
  dt();
  xI();
  We();
  ut();
  KW();
  yVr = He(() =>
    Ke.object({
      access_token: Ke.string(),
      expires_in: Ke.number(),
      refresh_token: Ke.string().nullish(),
    }),
  );
});
function XCn(e, t) {
  let n = Whi.dirname(t);
  return async (r) => {
    let o = await Xxd(n);
    try {
      return (q("tengu_wif_user_oauth_lock_acquired", {}), await e(r));
    } finally {
      q("tengu_wif_user_oauth_lock_released", {});
      try {
        await o();
      } catch (s) {
        if (Pd(s)) T(
