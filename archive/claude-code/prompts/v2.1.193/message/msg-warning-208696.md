---
id: msg-warning-208696
name: Warning Message
category: message
subcategory: warning
source_line: 208696
---

);
    return (
      Ie("keybinding_load_user_config"),
      { bindings: e.bindings, warnings: e.warnings }
    );
  } catch (r) {
    if (vn(r))
      return (
        Ie("keybinding_load_user_config"),
        (e.bindings = t),
        (e.warnings = []),
        { bindings: e.bindings, warnings: e.warnings }
      );
    return (
      T(
