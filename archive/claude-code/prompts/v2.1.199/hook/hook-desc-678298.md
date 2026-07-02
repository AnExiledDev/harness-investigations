---
id: hook-desc-678298
name: Hook Description
category: hook
subcategory: description
source_line: 678298
---

Input to command is JSON with task_id, task_subject, task_description, teammate_name, and team_name.
Exit code 0 - stdout/stderr not shown
Exit code 2 - show stderr to model and prevent task creation
Other exit codes - show stderr to user only
