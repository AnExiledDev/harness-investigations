---
id: hook-desc-644904
name: Hook Description
category: hook
subcategory: description
source_line: 644904
---

Input to command is JSON with expansion_type, command_name, command_args, command_source, and original prompt.
Exit code 0 - stdout shown to Claude
Exit code 2 - block expansion and show stderr to user only
Other exit codes - show stderr to user only
