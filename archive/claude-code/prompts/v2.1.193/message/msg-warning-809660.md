---
id: msg-warning-809660
name: Warning Message
category: message
subcategory: warning
source_line: 809660
---

,
    );
  return n;
}
var Kvc = E(() => {
  ut();
  Uf();
  $9();
  Nh();
  eL();
  Y_();
  Ge();
  kr();
  Ed();
  Tn();
});
async function yAe(e) {
  switch (e.kind) {
    case "session-start": {
      let t = await j9(e.source, {
          sessionId: e.sessionId,
          agentType: e.agentType,
          model: e.model,
          forceSyncExecution: e.forceSyncExecution,
        }),
        n = Gat();
      if (n) LVe(n);
      return t;
    }
    case "setup":
      return zZi(e.trigger, { forceSyncExecution: e.forceSyncExecution });
  }
}
var Tqo = E(() => {
  I0e();
  ha();
});
function Yvc() {
  return;
}
var wum;
var Xvc = E(() => {
  er();
  Ge();
  wum = {
    iterm: "iTerm",
    "iterm.app": "iTerm",
    ghostty: "Ghostty",
    kitty: "kitty",
    alacritty: "Alacritty",
    wezterm: "WezTerm",
    apple_terminal: "Terminal",
  };
});
class vqo {
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
async function Qvc() {
  try {
    let e = await Ave();
    if (!e) {
      T("Not in a GitHub repository, skipping path mapping update");
      return;
    }
    let t = mr(),
      r = vu(t) ?? t,
      o;
    try {
      o = Oy(await Jvc.realpath(r));
    } catch {
      o = r;
    }
    let s = e.toLowerCase(),
      a = Lt().githubRepoPaths?.[s] ?? [];
    if (a[0] === o) {
      T(
