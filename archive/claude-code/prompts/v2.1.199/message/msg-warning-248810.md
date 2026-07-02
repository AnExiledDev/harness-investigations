---
id: msg-warning-248810
name: Warning Message
category: message
subcategory: warning
source_line: 248810
---

;
        (console.warn(g), to(g, { level: "warn" }));
        continue;
      }
      d = f.fakeContent;
    }
    let p = r.write(u, d);
    o.push({ realPath: a, fakePath: p });
  }
  return { binds: o, degradeToDenyPaths: s };
}
var voe,
  Jaa,
  nco,
  dgp = "file:";
var Zaa = E(() => {
  CEe();
  ((voe = D(require("fs"))), (Jaa = require("os")), (nco = require("path")));
});
function sla(e) {
  if (e.caCertPath && e.caKeyPath)
    return ygp(e.caCertPath, e.caKeyPath, e.extraCaCertPaths);
  if (e.caCertPath || e.caKeyPath)
    throw Error(
      "tlsTerminate: caCertPath and caKeyPath must be provided together",
    );
  return _gp(e.extraCaCertPaths);
}
async function ila(e) {
  let t = new Set([IEe.dirname(e.trustBundlePath)]);
  if (e.ephemeral) t.add(IEe.dirname(e.certPath));
  for (let n of t)
    try {
      await rla.rm(n, { recursive: !0, force: !0 });
    } catch (r) {
      to(
