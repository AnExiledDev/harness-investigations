---
id: msg-warning-552758
name: Warning Message
category: message
subcategory: warning
source_line: 552758
---

;
            return { tool_use_id: t, type: "tool_result", content: n };
          }
        }
      },
    })));
  ((XSl = new WeakMap()), (JSl = new WeakMap()), (Q8t = new Map()));
});
function s7n(e, t) {
  let n = e ? t[e] : void 0,
    r = BS(n) ? n : void 0,
    o = !r && Kl(n) ? n : void 0;
  return { teammate: r, localAgent: o };
}
function eEl({
  viewingAgentTaskId: e,
  tasks: t,
  transcripts: n,
  mainIsBusy: r,
  mainConversationId: o,
}) {
  let { teammate: s, localAgent: i } = s7n(e, t),
    a = s ?? i;
  if (!a || !e) {
    let c = n[us()];
    return {
      task: void 0,
      isMain: !0,
      isTeammate: !1,
      messages: c?.messages ?? QSl,
      inProgressToolUseIDs: c?.inProgressToolUseIDs ?? ZSl,
      conversationKey: o,
      isLoading: r,
    };
  }
  let l = n[e];
  return {
    task: a,
    isMain: !1,
    isTeammate: !!s,
    messages: l?.messages ?? QSl,
    inProgressToolUseIDs: l?.inProgressToolUseIDs ?? ZSl,
    conversationKey: e,
    isLoading: a.status === "running" && !a.isIdle,
  };
}
var QSl, ZSl;
var bko = E(() => {
  ut();
  US();
  ((QSl = []), (ZSl = new Set()));
});
function hMe(e) {
  return s7n(e.viewingAgentTaskId, e.tasks).teammate;
}
function Z8t(e) {
  let { teammate: t, localAgent: n } = s7n(e.viewingAgentTaskId, e.tasks);
  if (t) return { type: "viewed", task: t };
  if (n) return { type: "named_agent", task: n };
  return { type: "leader" };
}
var e6t = E(() => {
  bko();
});
function H8e(e) {
  return e.type === "image" && e.content.length > 0;
}
function tEl(e) {
  if (!e) return;
  let t = Object.values(e)
    .filter(H8e)
    .map((n) => n.id);
  return t.length > 0 ? t : void 0;
}
function nEl(e, t, n) {
  let r = new Set(),
    o = 0,
    s = 0;
  for (let d of t) {
    if (d.type !== "attachment") continue;
    if ((o++, d.attachment.type !== "mcp_instructions_delta")) continue;
    s++;
    for (let p of d.attachment.addedNames) r.add(p);
    for (let p of d.attachment.removedNames) r.delete(p);
  }
  let i = e.filter((d) => d.type === "connected"),
    a = new Set(i.map((d) => d.name)),
    l = new Map();
  for (let d of i)
    if (d.instructions)
      l.set(
        d.name,
        
