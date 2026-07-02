---
id: msg-warning-823187
name: Warning Message
category: message
subcategory: warning
source_line: 823187
---

);
            continue;
          }
          const outputPath = path.join(OUTPUT_DIR, safeName);
          await fs.promises.writeFile(outputPath, fileBytes);
          console.log(\
