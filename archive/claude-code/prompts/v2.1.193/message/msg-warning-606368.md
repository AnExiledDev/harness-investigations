---
id: msg-warning-606368
name: Warning Message
category: message
subcategory: warning
source_line: 606368
---


          : D,
        pluginId: e,
        newVersion: b,
        oldVersion: c,
        alreadyUpToDate: !0,
        scope: s,
      };
    }
    C = await T6t(y, e, b, n, v, { forceOverwrite: x });
    let R = o.installPath;
    if ((THl(e, s, i, C, b, H, g?.version), R && R !== C)) {
      let D = aL();
      if (
        !Object.values(D.plugins).some((U) =>
          U.some((F) => F.installPath === R),
        )
      )
        await bMe(R);
    }
    let P = i ? 
