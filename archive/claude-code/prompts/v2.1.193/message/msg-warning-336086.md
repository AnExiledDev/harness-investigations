---
id: msg-warning-336086
name: Warning Message
category: message
subcategory: warning
source_line: 336086
---

);
  }
  return A1(
    {
      granted: y,
      denied: g,
      ...(f.length > 0 && { policyDenied: { apps: f, guidance: Rio(f) } }),
      ...(p.length > 0 && { userDenied: { apps: p, guidance: kio(p) } }),
      ...(_.length > 0 && { tierGuidance: nHa(_) }),
      screenshotFiltering: e.executor.capabilities.screenshotFiltering,
      ...(S.length > 0 ? { windowLocations: S } : {}),
    },
    { granted_count: m.length, denied_count: g.length, ...rHa(_) },
  );
}
async function udp(e, t) {
  if (t.length === 0) return [];
  let n = await e.executor.listDisplays();
  if (n.length <= 1) return [];
  let r = t.map((l) => l.bundleId),
    o = await e.executor.findWindowDisplays(r),
    s = new Map(n.map((l) => [l.displayId, l])),
    i = new Map(o.map((l) => [l.bundleId, l.displayIds])),
    a = [];
  for (let l of t) {
    let c = i.get(l.bundleId);
    if (!c || c.length === 0) continue;
    a.push({
      bundleId: l.bundleId,
      displayName: l.displayName,
      displays: c.map((u) => {
        let d = s.get(u);
        return { id: u, label: d?.label, isPrimary: d?.isPrimary };
      }),
    });
  }
  return a;
}
async function tHa(e, t, n, r, o) {
  let s = new Set(n.map((_) => _.bundleId)),
    i = await e.executor.listInstalledApps(),
    a = ldp(t, i, s),
    l = [],
    c = [];
  for (let _ of a) {
    let S = _.resolved?.displayName ?? _.requestedName;
    if (g1n(_.resolved?.bundleId, S))
      l.push({ requestedName: _.requestedName, displayName: S });
    else c.push(_);
  }
  let u = [],
    d = [];
  for (let _ of c)
    if (_.resolved && r.has(_.resolved.bundleId))
      u.push({
        requestedName: _.requestedName,
        displayName: _.resolved.displayName,
      });
    else d.push(_);
  let p = [];
  for (let _ of d) {
    if (_.proposedTier === "full" || !_.resolved) continue;
    p.push({
      bundleId: _.resolved.bundleId,
      displayName: _.resolved.displayName,
      tier: _.proposedTier,
    });
  }
  let f = d.filter((_) => _.alreadyGranted),
    m = d.filter((_) => !_.alreadyGranted);
  for (let _ of m) {
    if (!_.resolved) continue;
    try {
      _.resolved.iconDataUrl = await e.executor.getAppIcon(_.resolved.path);
    } catch {}
  }
  let g = Date.now(),
    h = f
      .filter((_) => _.resolved)
      .map(
        (_) =>
          n.find((H) => H.bundleId === _.resolved.bundleId) ?? {
            bundleId: _.resolved.bundleId,
            displayName: _.resolved.displayName,
            grantedAt: g,
            tier: _.proposedTier,
          },
      ),
    y = [
      ...n.map((_) => _.bundleId),
      ...d.filter((_) => _.resolved).map((_) => _.resolved.bundleId),
    ],
    b = await e.executor.previewHideSet(y, o);
  return {
    needDialog: m,
    skipDialogGrants: h,
    willHide: b,
    tieredApps: p,
    userDenied: u,
    policyDenied: l,
  };
}
function nHa(e) {
  let t = e.filter(
      (s) => s.tier === "read" && wct(s.bundleId, s.displayName) === "browser",
    ),
    n = e.filter(
      (s) => s.tier === "read" && wct(s.bundleId, s.displayName) !== "browser",
    ),
    r = e.filter((s) => s.tier === "click"),
    o = [];
  if (t.length > 0) {
    let s = t.map((i) => 
