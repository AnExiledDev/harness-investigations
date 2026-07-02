---
id: msg-warning-410370
name: Warning Message
category: message
subcategory: warning
source_line: 410370
---

,
            ),
            { status: "success" }
          );
      }
      if (
        (V("tengu_auto_updater_npm_failure", {
          npm_exit_code: s.code,
          package_manager: $e(t),
          is_bundled_mode: Qf(),
          platform: Yq(Wt()),
          windows_self_rename: $e(c),
          stderr_signature: $e(l),
          npm_error_code: M1p(a) ?? Ve("none"),
        }),
        Wt() === "windows" &&
          /\b(?:claude|cli)\.exe\b/i.test(a) &&
          (/\bEBUSY\b|resource busy or locked/i.test(a) ||
            (/\bEPERM\b|operation not permitted/i.test(a) &&
              (o.length > 0 ||
                /\b(?:rename|copyfile|unlink)\b[^\r\n]*\b(?:claude|cli)\.exe\b/i.test(
                  a,
                )))))
      )
        return (
          Re("update_apply", "update_apply_exe_locked"),
          T(
            
