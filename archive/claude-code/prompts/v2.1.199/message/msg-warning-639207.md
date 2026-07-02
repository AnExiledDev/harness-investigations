---
id: msg-warning-639207
name: Warning Message
category: message
subcategory: warning
source_line: 639207
---


          : R,
        pluginId: e,
        newVersion: _,
        oldVersion: c,
        alreadyUpToDate: !0,
        scope: s,
      };
    }
    I = await bZt(y, e, _, n, v, { forceOverwrite: x });
    let L = o.installPath;
    if ((F4l(e, s, i, I, _, H, g?.version), L && L !== I)) {
      let R = dD();
      if (
        !Object.values(R.plugins).some((j) =>
          j.some(($) => $.installPath === L),
        )
      )
        await RNe(L);
    }
    let P = i ? 
