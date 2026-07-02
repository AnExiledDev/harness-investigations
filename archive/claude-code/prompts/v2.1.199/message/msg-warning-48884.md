---
id: msg-warning-48884
name: Warning Message
category: message
subcategory: warning
source_line: 48884
---

), !0);
  };
  NPt = { assertOptions: zMu, validators: qhn };
});
class BPt {
  constructor(e) {
    ((this.defaults = e || {}),
      (this.interceptors = { request: new pMr(), response: new pMr() }));
  }
  async request(e, t) {
    try {
      return await this._request(e, t);
    } catch (n) {
      if (n instanceof Error) {
        let r = {};
        Error.captureStackTrace ? Error.captureStackTrace(r) : (r = Error());
        let o = (() => {
          if (!r.stack) return "";
          let s = r.stack.indexOf(
