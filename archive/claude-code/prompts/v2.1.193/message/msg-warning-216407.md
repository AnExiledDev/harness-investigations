---
id: msg-warning-216407
name: Warning Message
category: message
subcategory: warning
source_line: 216407
---


    );
  }
}
function Gzr() {
  return Lt().shiftEnterKeyBindingInstalled === !0;
}
function Wzr() {
  return Lt().hasUsedBackslashReturn === !0;
}
function Vzr() {
  if (!Lt().hasUsedBackslashReturn)
    mn((t) => ({ ...t, hasUsedBackslashReturn: !0 }));
}
async function cOd(e, t, n) {
  if (
    Ete.platform() === "darwin" &&
    process.env.__CFBundleIdentifier === "com.googlecode.iterm2" &&
    (Be.terminal === "iTerm.app" ||
      Be.terminal === "tmux" ||
      Be.terminal === "screen" ||
      Be.terminal === null)
  ) {
    let s = 
