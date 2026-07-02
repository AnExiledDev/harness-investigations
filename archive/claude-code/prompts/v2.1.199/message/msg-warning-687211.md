---
id: msg-warning-687211
name: Warning Message
category: message
subcategory: warning
source_line: 687211
---

] };
}
function Cnn(e, t) {
  let n = e.indexOf(".");
  return { type: "event", provider: e.slice(0, n), event: e, filter: t };
}
function jum(e) {
  if (!xnn(e)) return null;
  let t = typeof e.field === "string" ? e.field : "",
    n = typeof e.op === "string" ? e.op : "";
  if (!t || !n) return null;
  return { field: t, op: n, values: Inn(e.values) };
}
function Gum(e) {
  let t = e.trim();
  return t.startsWith("#") ? t.slice(1) : t;
}
function xnn(e) {
  return typeof e === "object" && e !== null && !Array.isArray(e);
}
function hzo(e) {
  if (e === void 0 || e === null) return [];
  return Array.isArray(e) ? e : [e];
}
function Inn(e) {
  return hzo(e)
    .map((t) => (typeof t === "string" ? t.trim() : ""))
    .filter((t) => t !== "");
}
function Wum(e) {
  switch (e.type) {
    case "cron":
      return 
