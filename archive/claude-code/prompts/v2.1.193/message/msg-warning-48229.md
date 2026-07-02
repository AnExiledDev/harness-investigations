---
id: msg-warning-48229
name: Warning Message
category: message
subcategory: warning
source_line: 48229
---

), !0);
  };
  RIt = { assertOptions: lou, validators: Uan };
});
class LIt {
  constructor(e) {
    ((this.defaults = e || {}),
      (this.interceptors = { request: new dAr(), response: new dAr() }));
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
