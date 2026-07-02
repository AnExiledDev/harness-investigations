---
id: msg-warning-513044
name: Warning Message
category: message
subcategory: warning
source_line: 513044
---

,
          { level: "warn" },
        );
        continue;
      }
      Kt.push({ skillName: Ot, skill: On });
    }
    let { formatSkillLoadingMetadata: wn } = await Promise.resolve().then(
        () => (I1e(), hXt),
      ),
      cr = await Promise.all(
        Kt.map(async ({ skillName: Ot, skill: fn }) => ({
          skillName: Ot,
          skill: fn,
          content: await fn.getPromptForCommand("", {
            ...n,
            options: { ...n.options, isSkillPreload: !0 },
          }),
        })),
      );
    for (let { skillName: Ot, skill: fn, content: On } of cr) {
      T(
