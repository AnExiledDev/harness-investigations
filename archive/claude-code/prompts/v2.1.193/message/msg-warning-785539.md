---
id: msg-warning-785539
name: Warning Message
category: message
subcategory: warning
source_line: 785539
---

);
            continue;
          }
          const outputPath = path.join(OUTPUT_DIR, safeName);
          await fs.promises.writeFile(outputPath, fileBytes);
          console.log(\
