---
id: msg-warning-466445
name: Warning Message
category: message
subcategory: warning
source_line: 466445
---

,
          { level: "warn" },
        );
        continue;
      }
      Dt.push({ skillName: dt, skill: Sn });
    }
    let { formatSkillLoadingMetadata: Qt } = await Promise.resolve().then(
        () => (Rgt(), PVt),
      ),
      Xn = await Promise.all(
        Dt.map(async ({ skillName: dt, skill: nn }) => ({
          skillName: dt,
          skill: nn,
          content: await nn.getPromptForCommand("", {
            ...n,
            options: { ...n.options, isSkillPreload: !0 },
          }),
        })),
      );
    for (let { skillName: dt, skill: nn, content: Sn } of Xn) {
      T(
