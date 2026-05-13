## SkillBraid

This project uses SkillBraid to store user-confirmed routes for recurring work.

Before deciding which skills, tools, or workflow to use for a non-trivial task, read:
- `.codex/skillbraid/SKILLBRAID.md`

Use a route only when its trigger conditions match the current request. Do not invent or force a route match.

If no confirmed route matches, proceed normally or propose a candidate route and wait for user confirmation before saving it.

When a confirmed route is used, end the response with:

```text
本次链路：...
选择原因：...
```

Do not create, update, or remove SkillBraid route rules unless the user confirms.
