---
id: msg-warning-319821
name: Warning Message
category: message
subcategory: warning
source_line: 319821
---

,
      ),
      []
    );
  }
}
function Zro(e) {
  return ufa.default().add(dfa).add(e);
}
function Onp(e, t = []) {
  return Zro(t).ignores(e);
}
function pfa(e, t = e, n = {}, r = []) {
  let o = eX.readdirSync(e),
    s = Zro(r);
  for (let i of o) {
    let a = Ice.join(e, i),
      l = Ice.relative(t, a);
    if (s.ignores(l)) continue;
    if (eX.statSync(a).isDirectory()) pfa(a, t, n, r);
    else {
      let u = l.split(Ice.sep).join("/");
      n[u] = eX.readFileSync(a);
    }
  }
  return n;
}
function I$n(e, t = e, n = {}, r = [], o = 0) {
  let s = eX.readdirSync(e),
    i = Zro(r);
  for (let a of s) {
    let l = Ice.join(e, a),
      c = Ice.relative(t, l);
    if (i.ignores(c)) {
      o++;
      continue;
    }
    let u = eX.statSync(l);
    if (u.isDirectory()) o = I$n(l, t, n, r, o).ignoredCount;
    else {
      let d = c.split(Ice.sep).join("/");
      n[d] = { data: eX.readFileSync(l), mode: u.mode };
    }
  }
  return { files: n, ignoredCount: o };
}
var eX, ufa, Ice, dfa;
var eoo = E(() => {
  ((eX = require("fs")),
    (ufa = L(fje(), 1)),
    (Ice = require("path")),
    (dfa = [
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
var eT = Q((too) => {
  too.fromCallback = function (e) {
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
  too.fromPromise = function (e) {
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
var wGe = Q((Y0e) => {
  var ffa = eT().fromCallback,
    aW = Rb(),
    Nnp = [
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
    ].filter((e) => typeof aW[e] === "function");
  Object.assign(Y0e, aW);
  Nnp.forEach((e) => {
    Y0e[e] = ffa(aW[e]);
  });
  Y0e.exists = function (e, t) {
    if (typeof t === "function") return aW.exists(e, t);
    return new Promise((n) => aW.exists(e, n));
  };
  Y0e.read = function (e, t, n, r, o, s) {
    if (typeof s === "function") return aW.read(e, t, n, r, o, s);
    return new Promise((i, a) => {
      aW.read(e, t, n, r, o, (l, c, u) => {
        if (l) return a(l);
        i({ bytesRead: c, buffer: u });
      });
    });
  };
  Y0e.write = function (e, t, ...n) {
    if (typeof n[n.length - 1] === "function") return aW.write(e, t, ...n);
    return new Promise((r, o) => {
      aW.write(e, t, ...n, (s, i, a) => {
        if (s) return o(s);
        r({ bytesWritten: i, buffer: a });
      });
    });
  };
  if (typeof aW.writev === "function")
    Y0e.writev = function (e, t, ...n) {
      if (typeof n[n.length - 1] === "function") return aW.writev(e, t, ...n);
      return new Promise((r, o) => {
        aW.writev(e, t, ...n, (s, i, a) => {
          if (s) return o(s);
          r({ bytesWritten: i, buffers: a });
        });
      });
    };
  if (typeof aW.realpath.native === "function")
    Y0e.realpath.native = ffa(aW.realpath.native);
  else
    process.emitWarning(
      "fs.realpath.native is not a function. Is fs being monkey-patched?",
      "Warning",
      "fs-extra-WARN0003",
    );
});
var gfa = Q((vvy, mfa) => {
  var Tvy = require("path");
  mfa.exports.checkPath = function (t) {};
});
var bfa = Q((wvy, noo) => {
  var hfa = wGe(),
    { checkPath: yfa } = gfa(),
    _fa = (e) => {
      let t = { mode: 511 };
      if (typeof e === "number") return e;
      return { ...t, ...e }.mode;
    };
  noo.exports.makeDir = async (e, t) => (
    yfa(e),
    hfa.mkdir(e, { mode: _fa(t), recursive: !0 })
  );
  noo.exports.makeDirSync = (e, t) => (
    yfa(e),
    hfa.mkdirSync(e, { mode: _fa(t), recursive: !0 })
  );
});
var ine = Q((Cvy, Sfa) => {
  var Bnp = eT().fromPromise,
    { makeDir: Fnp, makeDirSync: roo } = bfa(),
    ooo = Bnp(Fnp);
  Sfa.exports = {
    mkdirs: ooo,
    mkdirsSync: roo,
    mkdirp: ooo,
    mkdirpSync: roo,
    ensureDir: ooo,
    ensureDirSync: roo,
  };
});
var X0e = Q((Ivy, Hfa) => {
  var Unp = eT().fromPromise,
    Efa = wGe();
  function jnp(e) {
    return Efa.access(e)
      .then(() => !0)
      .catch(() => !1);
  }
  Hfa.exports = { pathExists: Unp(jnp), pathExistsSync: Efa.existsSync };
});
var soo = Q((xvy, Afa) => {
  var Flt = Rb();
  function Gnp(e, t, n, r) {
    Flt.open(e, "r+", (o, s) => {
      if (o) return r(o);
      Flt.futimes(s, t, n, (i) => {
        Flt.close(s, (a) => {
          if (r) r(i || a);
        });
      });
    });
  }
  function Wnp(e, t, n) {
    let r = Flt.openSync(e, "r+");
    return (Flt.futimesSync(r, t, n), Flt.closeSync(r));
  }
  Afa.exports = { utimesMillis: Gnp, utimesMillisSync: Wnp };
});
var CGe = Q((kvy, wfa) => {
  var Ult = wGe(),
    RM = require("path"),
    Vnp = require("util");
  function qnp(e, t, n) {
    let r = n.dereference
      ? (o) => Ult.stat(o, { bigint: !0 })
      : (o) => Ult.lstat(o, { bigint: !0 });
    return Promise.all([
      r(e),
      r(t).catch((o) => {
        if (o.code === "ENOENT") return null;
        throw o;
      }),
    ]).then(([o, s]) => ({ srcStat: o, destStat: s }));
  }
  function znp(e, t, n) {
    let r,
      o = n.dereference
        ? (i) => Ult.statSync(i, { bigint: !0 })
        : (i) => Ult.lstatSync(i, { bigint: !0 }),
      s = o(e);
    try {
      r = o(t);
    } catch (i) {
      if (i.code === "ENOENT") return { srcStat: s, destStat: null };
      throw i;
    }
    return { srcStat: s, destStat: r };
  }
  function Knp(e, t, n, r, o) {
    Vnp.callbackify(qnp)(e, t, r, (s, i) => {
      if (s) return o(s);
      let { srcStat: a, destStat: l } = i;
      if (l) {
        if (xUt(a, l)) {
          let c = RM.basename(e),
            u = RM.basename(t);
          if (n === "move" && c !== u && c.toLowerCase() === u.toLowerCase())
            return o(null, { srcStat: a, destStat: l, isChangingCase: !0 });
          return o(Error("Source and destination must not be the same."));
        }
        if (a.isDirectory() && !l.isDirectory())
          return o(
            Error(
              
