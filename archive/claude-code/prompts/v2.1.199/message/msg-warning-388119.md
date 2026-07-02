---
id: msg-warning-388119
name: Warning Message
category: message
subcategory: warning
source_line: 388119
---

,
      );
    return t;
  }
  fy.generateRandomPipeName = J9p;
  function Q9p(e, t = "utf-8") {
    let n,
      r = new Promise((o, s) => {
        n = o;
      });
    return new Promise((o, s) => {
      let i = (0, TVn.createServer)((a) => {
        (i.close(), n([new Oht(a, t), new Nht(a, t)]));
      });
      (i.on("error", s),
        i.listen(e, () => {
          (i.removeListener("error", s), o({ onConnected: () => r }));
        }));
    });
  }
  fy.createClientPipeTransport = Q9p;
  function Z9p(e, t = "utf-8") {
    let n = (0, TVn.createConnection)(e);
    return [new Oht(n, t), new Nht(n, t)];
  }
  fy.createServerPipeTransport = Z9p;
  function e8p(e, t = "utf-8") {
    let n,
      r = new Promise((o, s) => {
        n = o;
      });
    return new Promise((o, s) => {
      let i = (0, TVn.createServer)((a) => {
        (i.close(), n([new Oht(a, t), new Nht(a, t)]));
      });
      (i.on("error", s),
        i.listen(e, "127.0.0.1", () => {
          (i.removeListener("error", s), o({ onConnected: () => r }));
        }));
    });
  }
  fy.createClientSocketTransport = e8p;
  function t8p(e, t = "utf-8") {
    let n = (0, TVn.createConnection)(e, "127.0.0.1");
    return [new Oht(n, t), new Nht(n, t)];
  }
  fy.createServerSocketTransport = t8p;
  function n8p(e) {
    let t = e;
    return t.read !== void 0 && t.addListener !== void 0;
  }
  function r8p(e) {
    let t = e;
    return t.write !== void 0 && t.addListener !== void 0;
  }
  function o8p(e, t, n, r) {
    if (!n) n = Mz.NullLogger;
    let o = n8p(e) ? new rvo(e) : e,
      s = r8p(t) ? new ovo(t) : t;
    if (Mz.ConnectionStrategy.is(r)) r = { connectionStrategy: r };
    return (0, Mz.createMessageConnection)(o, s, n, r);
  }
  fy.createMessageConnection = o8p;
});
var d9a = J((zN_, u9a) => {
  u9a.exports = c9a();
});
var p9a = {};
lt(p9a, { createLSPClient: () => s8p });
function s8p(e, t) {
  let n,
    r,
    o,
    s = !1,
    i = !1,
    a,
    l = !1,
    c,
    u,
    d,
    p,
    f = [],
    m = [];
  function g() {
    if (i) throw a || Error(
