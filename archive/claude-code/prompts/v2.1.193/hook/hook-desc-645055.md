---
id: hook-desc-645055
name: Hook Description
category: hook
subcategory: description
source_line: 645055
---

Input to command is JSON with source (user_settings, project_settings, local_settings, policy_settings, skills) and file_path.
Exit code 0 - allow the change
Exit code 2 - block the change from being applied to the session
Other exit codes - show stderr to user only
