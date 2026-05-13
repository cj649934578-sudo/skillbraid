# SkillBraid

Weave Codex skills into reusable, explainable workflows.

将 Codex skills 编织成可解释、可复用、可持续优化的工作流。

SkillBraid is a Codex skill routing assistant. It scans installed skills, helps you design reusable skill chains, explains each route after use, and suggests confirmed improvements over time.

SkillBraid 是一个 Codex skill 路由助手：它会扫描你已安装的 skills，和你一起设计可复用的 skill 链路，在每次使用后说明本次链路，并根据使用情况提出可确认的优化建议。

## What it does

- Scans installed `SKILL.md` files.
- Classifies skills into capability groups.
- Surfaces hidden, invalid, and duplicate skills.
- Helps the user confirm recurring scenarios before writing route rules.
- Adds a short route explanation after routed answers.
- Suggests route improvements only when there is a clear reason.

## Verify

Run:

```powershell
python -m pytest tests/test_scan_skills.py tests/test_skill_package_files.py -v
```

Run the scanner directly:

```powershell
python scripts/scan_skills.py --json
```

## Install

Install this repository by copying or linking it into a Codex skill root such as `%USERPROFILE%\.codex\skills\skillbraid`.

After installation, ask Codex to initialize skill routing. The skill will scan installed skills, discuss common scenarios, and wait for confirmation before writing any route rules.
