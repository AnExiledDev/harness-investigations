---
id: msg-warning-584549
name: Warning Message
category: message
subcategory: warning
source_line: 584549
---

;
            return { tool_use_id: t, type: "tool_result", content: n };
          }
        }
      },
    })));
  ((ujl = new WeakMap()), (djl = new WeakMap()), (zQt = new Map()));
});
function Jsr(e, t) {
  let n = e ? t[e] : void 0,
    r = MS(n) ? n : void 0,
    o = !r && qa(n) ? n : void 0;
  return { teammate: r, localAgent: o };
}
function mjl({
  viewingAgentTaskId: e,
  tasks: t,
  transcripts: n,
  mainIsBusy: r,
  mainConversationId: o,
}) {
  let { teammate: s, localAgent: i } = Jsr(e, t),
    a = s ?? i;
  if (!a || !e) {
    let c = n[os()];
    return {
      task: void 0,
      isMain: !0,
      isTeammate: !1,
      messages: c?.messages ?? pjl,
      inProgressToolUseIDs: c?.inProgressToolUseIDs ?? fjl,
      conversationKey: o,
      isLoading: r,
    };
  }
  let l = n[e];
  return {
    task: a,
    isMain: !1,
    isTeammate: !!s,
    messages: l?.messages ?? pjl,
    inProgressToolUseIDs: l?.inProgressToolUseIDs ?? fjl,
    conversationKey: e,
    isLoading: a.status === "running" && !a.isIdle,
  };
}
var pjl, fjl;
var a4o = E(() => {
  dt();
  dy();
  ((pjl = []), (fjl = new Set()));
});
function CNe(e) {
  return Jsr(e.viewingAgentTaskId, e.tasks).teammate;
}
function KQt(e) {
  let { teammate: t, localAgent: n } = Jsr(e.viewingAgentTaskId, e.tasks);
  if (t) return { type: "viewed", task: t };
  if (n) return { type: "named_agent", task: n };
  return { type: "leader" };
}
var YQt = E(() => {
  a4o();
});
function N7e(e) {
  return e.type === "image" && e.content.length > 0;
}
function gjl(e) {
  if (!e) return;
  let t = Object.values(e)
    .filter(N7e)
    .map((n) => n.id);
  return t.length > 0 ? t : void 0;
}
function hjl(e, t, n) {
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
        
