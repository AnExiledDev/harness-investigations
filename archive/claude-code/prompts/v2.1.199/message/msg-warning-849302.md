---
id: msg-warning-849302
name: Warning Message
category: message
subcategory: warning
source_line: 849302
---

,
    );
  return n;
}
var Jqc = E(() => {
  dt();
  Uf();
  rz();
  OS();
  oM();
  X_();
  We();
  dr();
  ep();
  Cn();
});
async function Jwe(e) {
  switch (e.kind) {
    case "session-start": {
      let t = await pz(e.source, {
          sessionId: e.sessionId,
          agentType: e.agentType,
          model: e.model,
          forceSyncExecution: e.forceSyncExecution,
        }),
        n = Oft();
      if (n) wKe(n);
      return t;
    }
    case "setup":
      return WSa(e.trigger, { forceSyncExecution: e.forceSyncExecution });
  }
}
var Mos = E(() => {
  wPe();
  ya();
});
function Qqc() {
  return;
}
var W5m;
var Zqc = E(() => {
  Jn();
  We();
  W5m = {
    iterm: "iTerm",
    "iterm.app": "iTerm",
    ghostty: "Ghostty",
    kitty: "kitty",
    alacritty: "Alacritty",
    wezterm: "WezTerm",
    apple_terminal: "Terminal",
  };
});
class $os {
  frameDurations = [];
  totalFrames = 0;
  firstRenderTime;
  lastRenderTime;
  record(e) {
    let t = performance.now();
    if (this.firstRenderTime === void 0) this.firstRenderTime = t;
    if (
      ((this.lastRenderTime = t),
      this.totalFrames++,
      this.frameDurations.push(e),
      this.frameDurations.length > 3600)
    )
      this.frameDurations.splice(0, this.frameDurations.length >> 1);
  }
  getMetrics() {
    if (
      this.totalFrames === 0 ||
      this.firstRenderTime === void 0 ||
      this.lastRenderTime === void 0
    )
      return;
    let e = this.lastRenderTime - this.firstRenderTime;
    if (e <= 0) return;
    let t = this.totalFrames / (e / 1000),
      n = this.frameDurations.slice().sort((i, a) => a - i),
      r = Math.max(0, Math.ceil(n.length * 0.01) - 1),
      o = n[r],
      s = o > 0 ? 1000 / o : 0;
    return {
      averageFps: Math.round(t * 100) / 100,
      low1PctFps: Math.round(s * 100) / 100,
    };
  }
}
async function tVc() {
  try {
    let e = await _xe();
    if (!e) {
      T("Not in a GitHub repository, skipping path mapping update");
      return;
    }
    let t = ar(),
      r = gc(t) ?? t,
      o;
    try {
      o = Cy(await eVc.realpath(r));
    } catch {
      o = r;
    }
    let s = e.toLowerCase(),
      a = Dt().githubRepoPaths?.[s] ?? [];
    if (a[0] === o) {
      T(
