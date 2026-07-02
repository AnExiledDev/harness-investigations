---
id: msg-warning-677282
name: Warning Message
category: message
subcategory: warning
source_line: 677282
---

] };
}
function g7t(e, t) {
  let n = e.indexOf(".");
  return { type: "event", provider: e.slice(0, n), event: e, filter: t };
}
function YUf(e) {
  if (!y7t(e)) return null;
  let t = typeof e.field === "string" ? e.field : "",
    n = typeof e.op === "string" ? e.op : "";
  if (!t || !n) return null;
  return { field: t, op: n, values: h7t(e.values) };
}
function XUf(e) {
  let t = e.trim();
  return t.startsWith("#") ? t.slice(1) : t;
}
function y7t(e) {
  return typeof e === "object" && e !== null && !Array.isArray(e);
}
function FFo(e) {
  if (e === void 0 || e === null) return [];
  return Array.isArray(e) ? e : [e];
}
function h7t(e) {
  return FFo(e)
    .map((t) => (typeof t === "string" ? t.trim() : ""))
    .filter((t) => t !== "");
}
function JUf(e) {
  switch (e.type) {
    case "cron":
      return 
