---
id: msg-warning-767680
name: Warning Message
category: message
subcategory: warning
source_line: 767680
---

[TOKENS_MISSING] \${missing.length} CSS custom \${missing.length === 1 ? 'property' : 'properties'} referenced but not defined in shipped stylesheets: \${missing.slice(0, 8).join(', ')}\${missing.length > 8 ? ', \u2026' : ''}. Set cfg.tokensPkg (or cfg.tokensGlob) to the package that defines them, or cfg.provider if they're injected at runtime by a theme provider. Vars a component sets at runtime (inline style / JS) are EXPECTED to be absent here \u2014 check a rendered preview before chasing.\
