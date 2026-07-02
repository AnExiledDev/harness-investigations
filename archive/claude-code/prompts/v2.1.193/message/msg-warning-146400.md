---
id: msg-warning-146400
name: Warning Message
category: message
subcategory: warning
source_line: 146400
---

);
          return;
      }
    };
var cHn = E(() => {
  rD();
  gE();
  Yie();
  wCe();
  BBr();
  $di();
  iPt = Up("IdentityUtils");
});
function Gdi(e) {
  return zBr(
    [
      {
        name: "imdsRetryPolicy",
        retry: ({ retryCount: t, response: n }) => {
          if ((n === null || n === void 0 ? void 0 : n.status) !== 404)
            return { skipStrategy: !0 };
          return Soi(t, {
            retryDelayInMs: e.startDelayInMs,
            maxRetryDelayInMs: ocd,
          });
        },
      },
    ],
    { maxRetries: e.maxRetries },
  );
}
var ocd = 64000;
var Wdi = E(() => {
  Zie();
  wCe();
});
function acd(e) {
  var t;
  if (!vLt(e)) throw Error(
