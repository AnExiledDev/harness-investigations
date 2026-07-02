---
id: msg-warning-680701
name: Warning Message
category: message
subcategory: warning
source_line: 680701
---


          : "No obvious leak indicators. Check heap snapshot for retained objects.",
    },
    smapsRollup: u,
    objectTypeCounts: d,
    protectedObjectTypeCounts: p,
    mimalloc: f,
    platform: "linux",
    nodeVersion: process.version,
    ccVersion: {
      ISSUES_EXPLAINER:
        "report the issue at https://github.com/anthropics/claude-code/issues",
      PACKAGE_URL: "@anthropic-ai/claude-code",
      README_URL: "https://code.claude.com/docs/en/overview",
      VERSION: "2.1.199",
      FEEDBACK_CHANNEL: "https://github.com/anthropics/claude-code/issues",
      BUILD_TIME: "2026-07-02T01:14:04Z",
      GIT_SHA: "968b0c4118bde7c998acd97511e68daecacd8507",
      DD_SOURCEMAP_GROUP: "default",
    }.VERSION,
  };
}
async function C6o(e = "manual", t = 0) {
  try {
    let n = Rt(),
      r = await Klc(e, t),
      o = (d) => (d / 1024 / 1024 / 1024).toFixed(3);
    T(
