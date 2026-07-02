---
id: msg-warning-884888
name: Warning Message
category: message
subcategory: warning
source_line: 884888
---

);
    }
  }
  let u = new ReadableStream({
    async pull(d) {
      try {
        let p = await i.read();
        if (p.done) {
          (c(), d.close());
          return;
        }
        (a.push(p.value), d.enqueue(p.value));
      } catch (p) {
        (c(), d.error(p));
      }
    },
    async cancel(d) {
      (c(), await i.cancel(d));
    },
  });
  return new Response(u, {
    status: e.status,
    statusText: e.statusText,
    headers: e.headers,
  });
}
function FXm(e, t, n) {
  let r = new TextDecoder();
  if (e) {
    let a = "",
      l = GXm();
    return {
      push(c) {
        a += r.decode(c, { stream: !0 });
        let u = a.split(UXm);
        a = u.pop() ?? "";
        for (let d of u) Itu(l, d);
        if (a.length > Ctu) a = "";
      },
      async usage() {
        if (a !== "") (Itu(l, a), (a = ""));
        return WXm(l);
      },
    };
  }
  let o = "",
    s = 0,
    i = !1;
  return {
    push(a) {
      let l = r.decode(a, { stream: !0 });
      if (((s += l.length), i)) return;
      if (((o += l), o.length > Ctu)) ((i = !0), (o = ""));
    },
    async usage() {
      let a = i ? null : qXm(o);
      if (a) return a;
      if (s === 0) return null;
      return {
        input_tokens: (await t?.().catch(() => null)) ?? 0,
        output_tokens: Math.ceil(s / Rtu),
        speed: n,
      };
    },
  };
}
function GXm() {
  return {
    usage: { input_tokens: 0, output_tokens: 0 },
    seen: !1,
    estOutputChars: 0,
    sawOutputTokens: !1,
  };
}
function Itu(e, t) {
  let n = ucs(t, "event:"),
    r = n ? t.slice(n[0], n[1]).trim() : null;
  if (r === "content_block_delta") {
    xtu(e, t);
    return;
  }
  if (r !== null && r !== "message_start" && r !== "message_delta") return;
  if (r === null) {
    if (!t.includes('"usage"')) {
      if (t.includes('"content_block_delta"')) xtu(e, t);
      return;
    }
  }
  let o = ucs(t, "data:");
  if (!o) return;
  let s;
  try {
    s = JSON.parse(t.slice(o[0], o[1]).trim());
  } catch {
    return;
  }
  let i = VXm().safeParse(s);
  if (!i.success) return;
  if (i.data.type === "message_start" && i.data.message?.usage) {
    (Ltu(e.usage, i.data.message.usage), (e.seen = !0));
    return;
  }
  if (i.data.type === "content_block_delta" && i.data.delta) {
    let a = i.data.delta;
    e.estOutputChars +=
      (a.text?.length ?? 0) +
      (a.partial_json?.length ?? 0) +
      (a.thinking?.length ?? 0);
    return;
  }
  if (i.data.type === "message_delta" && i.data.usage) {
    if (i.data.usage.output_tokens !== void 0)
      ((e.usage.output_tokens = i.data.usage.output_tokens),
        (e.sawOutputTokens = !0));
    if (i.data.usage.server_tool_use !== void 0)
      e.usage.server_tool_use = i.data.usage.server_tool_use;
    e.seen = !0;
  }
}
function xtu(e, t) {
  let n = ucs(t, "data:");
  if (n) e.estOutputChars += Math.max(0, n[1] - n[0] - jXm);
}
function ucs(e, t) {
  let n = 0;
  while (!0) {
    if (e.startsWith(t, n)) {
      let o = n + t.length;
      if (e.charCodeAt(o) === 32) o += 1;
      let s = e.indexOf(
        
