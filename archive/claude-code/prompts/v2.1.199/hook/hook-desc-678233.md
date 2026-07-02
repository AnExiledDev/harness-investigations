---
id: hook-desc-678233
name: Hook Description
category: hook
subcategory: description
source_line: 678233
---

Input to command is JSON with agent_id, agent_type, and agent_transcript_path.
Exit code 0 - stdout/stderr not shown
Exit code 2 - show stderr to subagent and continue having it run
Other exit codes - show stderr to user only
