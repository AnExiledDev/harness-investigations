---
id: msg-warning-288354
name: Warning Message
category: message
subcategory: warning
source_line: 288354
---

);
  }
  return MN(
    {
      granted: y,
      denied: g,
      ...(f.length > 0 && { policyDenied: { apps: f, guidance: Ugo(f) } }),
      ...(p.length > 0 && { userDenied: { apps: p, guidance: Fgo(p) } }),
      ...(b.length > 0 && { tierGuidance: fAa(b) }),
      screenshotFiltering: e.executor.capabilities.screenshotFiltering,
      ...(S.length > 0 ? { windowLocations: S } : {}),
    },
    { granted_count: m.length, denied_count: g.length, ...mAa(b) },
  );
}
async function nIp(e, t) {
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
async function pAa(e, t, n, r, o) {
  let s = new Set(n.map((b) => b.bundleId)),
    i = await e.executor.listInstalledApps(),
    a = eIp(t, i, s),
    l = [],
    c = [];
  for (let b of a) {
    let S = b.resolved?.displayName ?? b.requestedName;
    if (c4n(b.resolved?.bundleId, S))
      l.push({ requestedName: b.requestedName, displayName: S });
    else c.push(b);
  }
  let u = [],
    d = [];
  for (let b of c)
    if (b.resolved && r.has(b.resolved.bundleId))
      u.push({
        requestedName: b.requestedName,
        displayName: b.resolved.displayName,
      });
    else d.push(b);
  let p = [];
  for (let b of d) {
    if (b.proposedTier === "full" || !b.resolved) continue;
    p.push({
      bundleId: b.resolved.bundleId,
      displayName: b.resolved.displayName,
      tier: b.proposedTier,
    });
  }
  let f = d.filter((b) => b.alreadyGranted),
    m = d.filter((b) => !b.alreadyGranted);
  for (let b of m) {
    if (!b.resolved) continue;
    try {
      b.resolved.iconDataUrl = await e.executor.getAppIcon(b.resolved.path);
    } catch {}
  }
  let g = Date.now(),
    h = f
      .filter((b) => b.resolved)
      .map(
        (b) =>
          n.find((H) => H.bundleId === b.resolved.bundleId) ?? {
            bundleId: b.resolved.bundleId,
            displayName: b.resolved.displayName,
            grantedAt: g,
            tier: b.proposedTier,
          },
      ),
    y = [
      ...n.map((b) => b.bundleId),
      ...d.filter((b) => b.resolved).map((b) => b.resolved.bundleId),
    ],
    _ = await e.executor.previewHideSet(y, o);
  return {
    needDialog: m,
    skipDialogGrants: h,
    willHide: _,
    tieredApps: p,
    userDenied: u,
    policyDenied: l,
  };
}
function fAa(e) {
  let t = e.filter(
      (s) => s.tier === "read" && Kft(s.bundleId, s.displayName) === "browser",
    ),
    n = e.filter(
      (s) => s.tier === "read" && Kft(s.bundleId, s.displayName) !== "browser",
    ),
    r = e.filter((s) => s.tier === "click"),
    o = [];
  if (t.length > 0) {
    let s = t.map((i) => 
