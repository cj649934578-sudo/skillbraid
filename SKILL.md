---
name: skillbraid
description: Use when the user asks to initialize skill routing, scan installed skills, create or maintain reusable skill chains, explain which skill route was used, or improve routes based on repeated usage. 将 Codex skills 编织成可解释、可复用、可持续优化的工作流。
---

# SkillBraid

Weave Codex skills into reusable, explainable workflows.

SkillBraid helps users manage many installed skills through confirmed, reusable skill chains. It routes, explains, and maintains chains; the selected domain skills still do the domain work.

SkillBraid 是一个 Codex skill 路由助手：它会扫描已安装的 skills，和用户一起设计可复用的 skill 链路，在每次使用后说明本次链路，并根据使用情况提出可确认的优化建议。

## Core Principles

- Prefer project route rules over global user preferences.
- Treat the user's explicit instruction in the current turn as the highest priority for that turn.
- Do not silently write or change route rules.
- Do not convert one-off instructions into permanent preferences without confirmation.
- Do not include invalid, unavailable, duplicate, or untriggerable skills in executable chains.
- Keep route explanations short unless the user asks for detailed reasoning.
- Store concise usage summaries only; do not store full sensitive prompts.
- Keep confirmed route triggers and chains in `SKILLBRAID.md`; do not hardcode route triggers in `AGENTS.md`.

## Route Explanation Guidance

When SkillBraid is active or explicitly invoked, read confirmed routes before choosing a skill chain.

当 SkillBraid 被触发或用户明确要求使用 SkillBraid 时，先读取用户确认过的链路规则，再判断本次链路，并在回答末尾输出：

```text
本次链路：...
选择原因：...
```

If a request does not match a confirmed route, propose a candidate route and wait for confirmation before treating it as standing behavior. If a higher-priority user instruction conflicts with a route, follow the user's current-turn instruction and briefly explain the conflict.

`AGENTS.md` should only point agents to SkillBraid rules. It should not duplicate route bodies or hardcode trigger categories that belong in `SKILLBRAID.md`.

## Storage Locations

Use these locations unless the user or project instructions specify another path:

- Global rules and usage notes: `%USERPROFILE%\.codex\skillbraid\SKILLBRAID.md`
- Project rules and usage notes: `.codex\skillbraid\SKILLBRAID.md`
- Project agent index: `AGENTS.md`

Before creating or updating any of these files, explain what will be written. Route rule changes require explicit user confirmation. Usage notes can be appended after initialization has been confirmed for the project, but each note must be concise.

Recommended `AGENTS.md` index:

```markdown
## SkillBraid

This project uses SkillBraid to store user-confirmed routes for recurring work.

Before deciding which skills, tools, or workflow to use for a non-trivial task, read:
- `.codex/skillbraid/SKILLBRAID.md`

Use a route only when its trigger conditions match the current request. Do not invent or force a route match.

If no confirmed route matches, proceed normally or propose a candidate route and wait for user confirmation before saving it.

When a confirmed route is used, end the response with:

本次链路：...
选择原因：...

Do not create, update, or remove SkillBraid route rules unless the user confirms.
```

## Command Triggers

Recognize these explicit commands:

- `skillbraid:init`
  - Initialize project SkillBraid guidance.
  - Scan installed skills, create or refresh `.codex/skillbraid/SKILLBRAID.md` after confirmation, and ask whether to add the `AGENTS.md` index.
- `skillbraid:update`
  - Update the current project's SkillBraid state.
  - Rescan skills, check confirmed routes, suggest improvements, and write changes only after confirmation.
- `skillbraid:update global`
  - Update `%USERPROFILE%\.codex\skillbraid\SKILLBRAID.md` after confirmation.
- `skillbraid:update route <route-name>`
  - Update one confirmed route by name.
  - Find the route in project rules first, then global rules, and write the change back to the same layer after confirmation.
- `skillbraid:help`
  - Explain commands, storage paths, the `AGENTS.md` index, and manual `SKILLBRAID.md` maintenance.

## Initialization Mode

Use initialization mode when the user asks to initialize, set up, scan, map, or configure skill routing.

1. Announce that you are scanning installed skills and building a capability map.
2. Scan all usable installed skill roots, not only the skills already visible in the current prompt.
3. If the current prompt includes a visible skill list, pass those names to the scanner with `--visible-names`.
4. Run the scanner:

```powershell
python scripts/scan_skills.py --json
```

5. If the user provides additional roots, run the scanner with explicit roots:

```powershell
python scripts/scan_skills.py --roots <root-1> <root-2> --json
```

6. Classify results into:
   - visible and triggerable skills
   - installed but not visible skills
   - invalid skills
   - duplicate skill names
7. Present a concise capability map with strong areas, overlapping areas, gaps, and unavailable skills.
8. Create or update `.codex/skillbraid/SKILLBRAID.md` only after explaining the file and receiving confirmation.
9. Ask whether to add or refresh the `AGENTS.md` SkillBraid index. Keep it as an index only.
10. Ask about one recurring user scenario at a time.
11. For each confirmed scenario, propose a candidate route with trigger conditions, skip conditions, chain order, reasons, and risks.
12. Write route rules only after the user confirms the exact route and storage layer.

## Daily Routing Mode

Use daily routing mode when the user asks for work that may match an existing route.

1. Read `.codex/skillbraid/SKILLBRAID.md` first if it exists.
2. Read `%USERPROFILE%\.codex\skillbraid\SKILLBRAID.md` second if it exists.
3. Treat `AGENTS.md` as an index only; do not treat it as the source of route triggers or route bodies.
4. Apply this priority:
   - current-turn explicit user instruction
   - project route rules
   - global user preferences
   - session judgment
5. If a route matches, follow it and keep moving.
6. If the request is a new scenario, propose one candidate route and wait for confirmation before treating it as a standing route.
7. If multiple routes match, explain the conflict briefly and prefer the project route unless the user says otherwise.
8. If a needed skill is missing, installed but hidden, invalid, or duplicated, state the gap and help the user search for or install a suitable skill.
9. If the user explicitly names a skill, respect that choice and explain how it relates to the route.

End routed answers with:

```text
本次链路：skill-a -> skill-b -> skill-c
选择原因：一句话说明为什么这样走。
```

## Continuous Optimization

Track concise usage notes after routed work when route storage has been initialized.

Useful signals:

- similar requests appear repeatedly without a stable route
- an existing route often needs the same temporary extra skill
- the user often skips, overrides, or shortens a route
- a scenario repeatedly exposes missing skill coverage
- project rules and global preferences often conflict

Only suggest a change when the suggestion is specific, easy to reject, and includes a reason.

Use this format:

```text
后续可选优化：最近类似需求多次临时补用了 accessibility。
原因：这说明 accessibility 已经变成前端链路中的稳定质量检查环节。
建议：是否把 accessibility 加入「前端实现」常用链路？
```

Do not write the change until the user confirms.

## Route Proposal Format

When proposing a route for a confirmed scenario, use:

```text
场景：<short scenario name>
触发条件：<when this route should run>
跳过条件：<when this route should not run>
候选链路：skill-a -> skill-b -> skill-c
原因：<why this order fits>
风险：<what could go wrong or become noisy>
写入位置建议：project / global
```

Ask for confirmation before writing the rule.

## Reference Files

- `references/capability-groups.json` defines scanner grouping keywords.
- `references/SKILLBRAID.template.md` shows the Markdown route and usage-note structure.
- `references/AGENTS.skillbraid.md` shows the recommended `AGENTS.md` index block.
