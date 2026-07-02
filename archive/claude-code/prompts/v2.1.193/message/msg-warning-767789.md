---
id: msg-warning-767789
name: Warning Message
category: message
subcategory: warning
source_line: 767789
---

);
  }
} catch { /* heuristic only \u2014 never block validation on a font-parse hiccup */ }

// README + per-component files. Parity with the app's self-check: each
// preview's first line must be the @dsCard comment (else the DS pane never
// registers the card), its <link href> targets must resolve (else previews
// render unstyled), and each .prompt.md's first line must be non-empty (it's
// the element-index summary).
if (!existsSync(join(OUT, 'README.md'))) fail('README.md missing');
let previews = 0, prompts = 0, badCard = 0, badLink = 0, badPrompt = 0;
(function walk(d) {
  if (!existsSync(d)) return;
  for (const e of readdirSync(d, { withFileTypes: true })) {
    const p = join(d, e.name);
    if (e.isDirectory()) { walk(p); continue; }
    const rel = relOut(p);
    if (e.name.endsWith('.html')) {
      previews++;
      const txt = readFileSync(p, 'utf8');
      // group is required; further attributes (viewport="WxH" on single-mode
      // cards, name/subtitle on hand-authored ones) are allowed after it.
      if (!/^<!--\\s*@dsCard\\s+group="[^"]*"[^>]*-->/.test(txt.split('\\n', 1)[0])) {
        badCard++; fail(\
