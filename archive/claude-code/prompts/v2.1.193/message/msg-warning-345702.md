---
id: msg-warning-345702
name: Warning Message
category: message
subcategory: warning
source_line: 345702
---

,
      );
    return t;
  }
  Mh.generateRandomPipeName = yfp;
  function _fp(e, t = "utf-8") {
    let n,
      r = new Promise((o, s) => {
        n = o;
      });
    return new Promise((o, s) => {
      let i = (0, rNn.createServer)((a) => {
        (i.close(), n([new Jct(a, t), new Qct(a, t)]));
      });
      (i.on("error", s),
        i.listen(e, () => {
          (i.removeListener("error", s), o({ onConnected: () => r }));
        }));
    });
  }
  Mh.createClientPipeTransport = _fp;
  function bfp(e, t = "utf-8") {
    let n = (0, rNn.createConnection)(e);
    return [new Jct(n, t), new Qct(n, t)];
  }
  Mh.createServerPipeTransport = bfp;
  function Sfp(e, t = "utf-8") {
    let n,
      r = new Promise((o, s) => {
        n = o;
      });
    return new Promise((o, s) => {
      let i = (0, rNn.createServer)((a) => {
        (i.close(), n([new Jct(a, t), new Qct(a, t)]));
      });
      (i.on("error", s),
        i.listen(e, "127.0.0.1", () => {
          (i.removeListener("error", s), o({ onConnected: () => r }));
        }));
    });
  }
  Mh.createClientSocketTransport = Sfp;
  function Efp(e, t = "utf-8") {
    let n = (0, rNn.createConnection)(e, "127.0.0.1");
    return [new Jct(n, t), new Qct(n, t)];
  }
  Mh.createServerSocketTransport = Efp;
  function Hfp(e) {
    let t = e;
    return t.read !== void 0 && t.addListener !== void 0;
  }
  function Afp(e) {
    let t = e;
    return t.write !== void 0 && t.addListener !== void 0;
  }
  function Tfp(e, t, n, r) {
    if (!n) n = o8.NullLogger;
    let o = Hfp(e) ? new Qao(e) : e,
      s = Afp(t) ? new Zao(t) : t;
    if (o8.ConnectionStrategy.is(r)) r = { connectionStrategy: r };
    return (0, o8.createMessageConnection)(o, s, n, r);
  }
  Mh.createMessageConnection = Tfp;
});
var JTa = Q((NBy, XTa) => {
  XTa.exports = YTa();
});
var ZTa = {};
gt(ZTa, { createLSPClient: () => vfp });
function vfp(e, t) {
  let n,
    r,
    o,
    s = !1,
    i = !1,
    a,
    l = !1,
    c = [],
    u = [];
  function d() {
    if (i) throw a || Error(
