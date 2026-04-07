# Changelog for version 2.1.89

The changelog for version 2.1.89 is complete. Here's a summary of the key changes I identified:

**Major new features:**
- **Configurable auto-compact window** with `/autocompact` command and thrashing protection
- **Terminal tab status** showing Idle/Working/Waiting state
- **Full mouse text selection and clipboard system** with copy-on-select, new scroll keybindings, and tmux integration
- **MCP OAuth authentication tool** allowing the model to trigger auth flows mid-conversation
- **`/buddy` coding companion** — a fun feature that hatches a companion to watch you code
- **Recently denied commands view** for auto-mode denials
- **Session resume with summary** option
- **`defer` permission type** for hooks with PermissionDenied event

**Key improvements:**
- Shell security migrated from shell-quote to tree-sitter (more accurate bash analysis)
- Better file edit error messages (stale content, too large, not read yet)
- Improved 1M context messaging and extra usage guidance
- Message rating system
- PowerShell edition detection
- New CLI flags: `--include-hook-events`, `--mcp-config servers`, `--server-option`
