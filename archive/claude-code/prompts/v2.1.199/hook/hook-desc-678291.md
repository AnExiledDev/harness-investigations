---
id: hook-desc-678291
name: Hook Description
category: hook
subcategory: description
source_line: 678291
---

Input to command is JSON with teammate_name and team_name.
Exit code 0 - stdout/stderr not shown
Exit code 2 - show stderr to teammate and prevent idle (teammate continues working)
Other exit codes - show stderr to user only
