---
id: msg-warning-697683
name: Warning Message
category: message
subcategory: warning
source_line: 697683
---

);
    (console.warn(
      "Tool registration will proceed, but this may cause compatibility issues.",
    ),
      console.warn(
        "Consider updating the tool name to conform to the MCP tool naming standard.",
      ),
      console.warn(
        "See SEP: Specify Format for Tool Names (https://github.com/modelcontextprotocol/modelcontextprotocol/issues/986) for more details.",
      ));
  }
}
function $Ko(e) {
  let t = rmm(e);
  return (omm(e, t.warnings), t.isValid);
}
var nmm;
var wmc = E(() => {
  nmm = /^[A-Za-z0-9._-]{1,128}$/;
});
class OKo {
  constructor(e) {
    this._mcpServer = e;
  }
  registerToolTask(e, t, n) {
    let r = { taskSupport: "required", ...t.execution };
    if (r.taskSupport === "forbidden")
      throw Error(
        
