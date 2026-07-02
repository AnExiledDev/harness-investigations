---
id: msg-warning-149260
name: Warning Message
category: message
subcategory: warning
source_line: 149260
---

);
          return;
      }
    };
var f0n = E(() => {
  uP();
  oA();
  Gce();
  S0e();
  j8r();
  Y0i();
  AFt = sf("IdentityUtils");
});
function nRi(e) {
  return X8r(
    [
      {
        name: "imdsRetryPolicy",
        retry: ({ retryCount: t, response: n }) => {
          if ((n === null || n === void 0 ? void 0 : n.status) !== 404)
            return { skipStrategy: !0 };
          return DTi(t, {
            retryDelayInMs: e.startDelayInMs,
            maxRetryDelayInMs: RFd,
          });
        },
      },
    ],
    { maxRetries: e.maxRetries },
  );
}
var RFd = 64000;
var rRi = E(() => {
  zce();
  S0e();
});
function PFd(e) {
  var t;
  if (!UNt(e)) throw Error(
