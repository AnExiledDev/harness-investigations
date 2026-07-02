---
id: msg-warning-460029
name: Warning Message
category: message
subcategory: warning
source_line: 460029
---

,
            ),
            { status: "success" }
          );
      }
      if (
        (q("tengu_auto_updater_npm_failure", {
          npm_exit_code: s.code,
          package_manager: Me(t),
          is_bundled_mode: of(),
          platform: f6(Wt()),
          windows_self_rename: Me(c),
          stderr_signature: Me(l),
          npm_error_code: Ryf(a) ?? Ve("none"),
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
          Ie("update_apply", "update_apply_exe_locked"),
          T(
            
