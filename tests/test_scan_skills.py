import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from scan_skills import build_summary, scan_skill_roots


def write_skill(root: Path, relative_dir: str, name: str, description: str) -> Path:
    skill_dir = root / relative_dir
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        f"""---
name: {name}
description: "{description}"
---

# {name}
""",
        encoding="utf-8",
    )
    return skill_file


def test_scan_skill_roots_reports_visibility_duplicates_and_invalid(tmp_path: Path):
    root = tmp_path / "skills"
    write_skill(root, "frontend", "frontend-design", "Create production-grade frontend interfaces")
    write_skill(root, "docs", "quiet-docs", "Write concise project documentation")
    write_skill(root, "dupe-a", "duplicate-route", "First duplicate skill")
    write_skill(root, "dupe-b", "duplicate-route", "Second duplicate skill")

    invalid_dir = root / "invalid"
    invalid_dir.mkdir(parents=True)
    (invalid_dir / "SKILL.md").write_text(
        """---
name: invalid-skill
---

# Missing description
""",
        encoding="utf-8",
    )

    records = scan_skill_roots(
        [root],
        visible_names={"frontend-design"},
        capability_groups={
            "frontend and design": ["frontend", "interface"],
            "documentation": ["documentation", "docs"],
        },
    )

    by_name = {}
    for record in records:
        by_name.setdefault(record.name, []).append(record)

    assert by_name["frontend-design"][0].status == "visible"
    assert by_name["quiet-docs"][0].status == "installed_not_visible"
    assert by_name["invalid-skill"][0].status == "invalid"
    assert "missing_description" in by_name["invalid-skill"][0].problems

    duplicate_records = by_name["duplicate-route"]
    assert len(duplicate_records) == 2
    assert {record.status for record in duplicate_records} == {"duplicate"}
    assert all("duplicate_name" in record.problems for record in duplicate_records)


def test_build_summary_counts_statuses_and_groups(tmp_path: Path):
    root = tmp_path / "skills"
    write_skill(root, "frontend", "frontend-design", "Create frontend UI")
    write_skill(root, "testing", "test", "Generate or run tests")

    records = scan_skill_roots(
        [root],
        visible_names={"frontend-design", "test"},
        capability_groups={
            "frontend and design": ["frontend", "ui"],
            "testing": ["test", "pytest"],
        },
    )

    summary = build_summary(records)

    assert summary["statuses"]["visible"] == 2
    assert summary["groups"]["frontend and design"] == 1
    assert summary["groups"]["testing"] == 1
    assert summary["total_records"] == 2


def test_capability_group_matching_uses_token_boundaries(tmp_path: Path):
    root = tmp_path / "skills"
    write_skill(
        root,
        "scanner",
        "scanner-audit",
        "Review using a suite to inspect scanner behavior and run tests",
    )

    records = scan_skill_roots(
        [root],
        capability_groups={
            "frontend and design": ["ui"],
            "planning": ["spec"],
            "testing": ["tests"],
        },
    )

    assert records[0].capability_groups == ["testing"]


def test_scan_skill_roots_parses_folded_yaml_descriptions(tmp_path: Path):
    root = tmp_path / "skills"
    skill_dir = root / "code-optimizer"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: code-optimizer
description: >-
  Deep code optimization audit using parallel agents.
  Use when performance matters.
---

# code-optimizer
""",
        encoding="utf-8",
    )

    records = scan_skill_roots([root])

    assert records[0].description == (
        "Deep code optimization audit using parallel agents. Use when performance matters."
    )
    assert records[0].status != "invalid"


def test_scan_skill_roots_dedupes_overlapping_roots(tmp_path: Path):
    parent = tmp_path / "skills"
    write_skill(parent, ".system/imagegen", "imagegen", "Generate raster images")

    records = scan_skill_roots([parent, parent / ".system"])
    imagegen_records = [record for record in records if record.name == "imagegen"]

    assert len(imagegen_records) == 1
    assert imagegen_records[0].status != "duplicate"


def test_cli_outputs_json_summary(tmp_path: Path):
    root = tmp_path / "skills"
    groups_file = tmp_path / "groups.json"
    write_skill(root, "planning", "brainstorming", "Explore ideas before implementation")
    groups_file.write_text(
        json.dumps({"planning": ["brainstorming", "ideas"]}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "scan_skills.py"),
            "--roots",
            str(root),
            "--visible-names",
            "brainstorming",
            "--groups",
            str(groups_file),
            "--json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)

    assert payload["summary"]["total_records"] == 1
    assert payload["records"][0]["name"] == "brainstorming"
    assert payload["records"][0]["status"] == "visible"
    assert payload["records"][0]["capability_groups"] == ["planning"]
