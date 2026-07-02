---
id: msg-warning-366561
name: Warning Message
category: message
subcategory: warning
source_line: 366561
---

,
      ),
      []
    );
  }
}
function jEo(e) {
  return yUa.default().add(_Ua).add(e);
}
function D2p(e, t = []) {
  return jEo(t).ignores(e);
}
function bUa(e, t = e, n = {}, r = []) {
  let o = jQ.readdirSync(e),
    s = jEo(r);
  for (let i of o) {
    let a = zpe.join(e, i),
      l = zpe.relative(t, a);
    if (s.ignores(l)) continue;
    if (jQ.statSync(a).isDirectory()) bUa(a, t, n, r);
    else {
      let u = l.split(zpe.sep).join("/");
      n[u] = jQ.readFileSync(a);
    }
  }
  return n;
}
function f5n(e, t = e, n = {}, r = [], o = 0) {
  let s = jQ.readdirSync(e),
    i = jEo(r);
  for (let a of s) {
    let l = zpe.join(e, a),
      c = zpe.relative(t, l);
    if (i.ignores(c)) {
      o++;
      continue;
    }
    let u = jQ.statSync(l);
    if (u.isDirectory()) o = f5n(l, t, n, r, o).ignoredCount;
    else {
      let d = c.split(zpe.sep).join("/");
      n[d] = { data: jQ.readFileSync(l), mode: u.mode };
    }
  }
  return { files: n, ignoredCount: o };
}
var jQ, yUa, zpe, _Ua;
var GEo = E(() => {
  ((jQ = require("fs")),
    (yUa = D(s5e(), 1)),
    (zpe = require("path")),
    (_Ua = [
      ".DS_Store",
      "Thumbs.db",
      ".gitignore",
      ".git",
      ".mcpbignore",
      "*.log",
      ".env*",
      ".npm",
      ".npmrc",
      ".yarnrc",
      ".yarn",
      ".eslintrc",
      ".editorconfig",
      ".prettierrc",
      ".prettierignore",
      ".eslintignore",
      ".nycrc",
      ".babelrc",
      ".pnp.*",
      "node_modules/.cache",
      "node_modules/.bin",
      "*.map",
      ".env.local",
      ".env.*.local",
      "npm-debug.log*",
      "yarn-debug.log*",
      "yarn-error.log*",
      "package-lock.json",
      "yarn.lock",
      "*.mcpb",
      "*.d.ts",
      "*.tsbuildinfo",
      "tsconfig.json",
    ]));
});
var jT = J((WEo) => {
  WEo.fromCallback = function (e) {
    return Object.defineProperty(
      function (...t) {
        if (typeof t[t.length - 1] === "function") e.apply(this, t);
        else
          return new Promise((n, r) => {
            (t.push((o, s) => (o != null ? r(o) : n(s))), e.apply(this, t));
          });
      },
      "name",
      { value: e.name },
    );
  };
  WEo.fromPromise = function (e) {
    return Object.defineProperty(
      function (...t) {
        let n = t[t.length - 1];
        if (typeof n !== "function") return e.apply(this, t);
        else (t.pop(), e.apply(this, t).then((r) => n(null, r), n));
      },
      "name",
      { value: e.name },
    );
  };
});
var _8e = J((NMe) => {
  var SUa = jT().fromCallback,
    Sq = yS(),
    P2p = [
      "access",
      "appendFile",
      "chmod",
      "chown",
      "close",
      "copyFile",
      "fchmod",
      "fchown",
      "fdatasync",
      "fstat",
      "fsync",
      "ftruncate",
      "futimes",
      "lchmod",
      "lchown",
      "link",
      "lstat",
      "mkdir",
      "mkdtemp",
      "open",
      "opendir",
      "readdir",
      "readFile",
      "readlink",
      "realpath",
      "rename",
      "rm",
      "rmdir",
      "stat",
      "symlink",
      "truncate",
      "unlink",
      "utimes",
      "writeFile",
    ].filter((e) => typeof Sq[e] === "function");
  Object.assign(NMe, Sq);
  P2p.forEach((e) => {
    NMe[e] = SUa(Sq[e]);
  });
  NMe.exists = function (e, t) {
    if (typeof t === "function") return Sq.exists(e, t);
    return new Promise((n) => Sq.exists(e, n));
  };
  NMe.read = function (e, t, n, r, o, s) {
    if (typeof s === "function") return Sq.read(e, t, n, r, o, s);
    return new Promise((i, a) => {
      Sq.read(e, t, n, r, o, (l, c, u) => {
        if (l) return a(l);
        i({ bytesRead: c, buffer: u });
      });
    });
  };
  NMe.write = function (e, t, ...n) {
    if (typeof n[n.length - 1] === "function") return Sq.write(e, t, ...n);
    return new Promise((r, o) => {
      Sq.write(e, t, ...n, (s, i, a) => {
        if (s) return o(s);
        r({ bytesWritten: i, buffer: a });
      });
    });
  };
  if (typeof Sq.writev === "function")
    NMe.writev = function (e, t, ...n) {
      if (typeof n[n.length - 1] === "function") return Sq.writev(e, t, ...n);
      return new Promise((r, o) => {
        Sq.writev(e, t, ...n, (s, i, a) => {
          if (s) return o(s);
          r({ bytesWritten: i, buffers: a });
        });
      });
    };
  if (typeof Sq.realpath.native === "function")
    NMe.realpath.native = SUa(Sq.realpath.native);
  else
    process.emitWarning(
      "fs.realpath.native is not a function. Is fs being monkey-patched?",
      "Warning",
      "fs-extra-WARN0003",
    );
});
var AUa = J((_w_, EUa) => {
  var yw_ = require("path");
  EUa.exports.checkPath = function (t) {};
});
var wUa = J((bw_, qEo) => {
  var HUa = _8e(),
    { checkPath: TUa } = AUa(),
    vUa = (e) => {
      let t = { mode: 511 };
      if (typeof e === "number") return e;
      return { ...t, ...e }.mode;
    };
  qEo.exports.makeDir = async (e, t) => (
    TUa(e),
    HUa.mkdir(e, { mode: vUa(t), recursive: !0 })
  );
  qEo.exports.makeDirSync = (e, t) => (
    TUa(e),
    HUa.mkdirSync(e, { mode: vUa(t), recursive: !0 })
  );
});
var ose = J((Sw_, CUa) => {
  var M2p = jT().fromPromise,
    { makeDir: $2p, makeDirSync: VEo } = wUa(),
    zEo = M2p($2p);
  CUa.exports = {
    mkdirs: zEo,
    mkdirsSync: VEo,
    mkdirp: zEo,
    mkdirpSync: VEo,
    ensureDir: zEo,
    ensureDirSync: VEo,
  };
});
var BMe = J((Ew_, xUa) => {
  var O2p = jT().fromPromise,
    IUa = _8e();
  function N2p(e) {
    return IUa.access(e)
      .then(() => !0)
      .catch(() => !1);
  }
  xUa.exports = { pathExists: O2p(N2p), pathExistsSync: IUa.existsSync };
});
var KEo = J((Aw_, kUa) => {
  var Ngt = yS();
  function B2p(e, t, n, r) {
    Ngt.open(e, "r+", (o, s) => {
      if (o) return r(o);
      Ngt.futimes(s, t, n, (i) => {
        Ngt.close(s, (a) => {
          if (r) r(i || a);
        });
      });
    });
  }
  function F2p(e, t, n) {
    let r = Ngt.openSync(e, "r+");
    return (Ngt.futimesSync(r, t, n), Ngt.closeSync(r));
  }
  kUa.exports = { utimesMillis: B2p, utimesMillisSync: F2p };
});
var b8e = J((Hw_, DUa) => {
  var Bgt = _8e(),
    cO = require("path"),
    U2p = require("util");
  function j2p(e, t, n) {
    let r = n.dereference
      ? (o) => Bgt.stat(o, { bigint: !0 })
      : (o) => Bgt.lstat(o, { bigint: !0 });
    return Promise.all([
      r(e),
      r(t).catch((o) => {
        if (o.code === "ENOENT") return null;
        throw o;
      }),
    ]).then(([o, s]) => ({ srcStat: o, destStat: s }));
  }
  function G2p(e, t, n) {
    let r,
      o = n.dereference
        ? (i) => Bgt.statSync(i, { bigint: !0 })
        : (i) => Bgt.lstatSync(i, { bigint: !0 }),
      s = o(e);
    try {
      r = o(t);
    } catch (i) {
      if (i.code === "ENOENT") return { srcStat: s, destStat: null };
      throw i;
    }
    return { srcStat: s, destStat: r };
  }
  function W2p(e, t, n, r, o) {
    U2p.callbackify(j2p)(e, t, r, (s, i) => {
      if (s) return o(s);
      let { srcStat: a, destStat: l } = i;
      if (l) {
        if (e9t(a, l)) {
          let c = cO.basename(e),
            u = cO.basename(t);
          if (n === "move" && c !== u && c.toLowerCase() === u.toLowerCase())
            return o(null, { srcStat: a, destStat: l, isChangingCase: !0 });
          return o(Error("Source and destination must not be the same."));
        }
        if (a.isDirectory() && !l.isDirectory())
          return o(
            Error(
              
