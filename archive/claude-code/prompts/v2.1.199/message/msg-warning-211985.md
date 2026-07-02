---
id: msg-warning-211985
name: Warning Message
category: message
subcategory: warning
source_line: 211985
---

);
    return (
      xe("keybinding_load_user_config"),
      { bindings: e.bindings, warnings: e.warnings }
    );
  } catch (r) {
    if (pn(r))
      return (
        xe("keybinding_load_user_config"),
        (e.bindings = t),
        (e.warnings = []),
        { bindings: e.bindings, warnings: e.warnings }
      );
    return (
      T(
