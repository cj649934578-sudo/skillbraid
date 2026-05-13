from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class SkillRecord:
    name: str
    description: str
    path: str
    root: str
    status: str
    problems: list[str] = field(default_factory=list)
    capability_groups: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "root": self.root,
            "status": self.status,
            "problems": list(self.problems),
            "capability_groups": list(self.capability_groups),
        }


def parse_frontmatter(skill_file: Path) -> tuple[dict[str, str], list[str]]:
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, ["missing_frontmatter"]

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["missing_frontmatter"]

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        return {}, ["unterminated_frontmatter"]

    metadata: dict[str, str] = {}
    frontmatter_lines = lines[1:end_index]
    index = 0
    while index < len(frontmatter_lines):
        line = frontmatter_lines[index]
        stripped = line.strip()
        index += 1
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">", ">-", ">+", "|", "|-", "|+"}:
            block_lines: list[str] = []
            while index < len(frontmatter_lines):
                block_line = frontmatter_lines[index]
                if block_line.strip() and not block_line.startswith((" ", "\t")):
                    break
                block_lines.append(block_line.lstrip())
                index += 1
            if value.startswith(">"):
                metadata[key] = " ".join(line.strip() for line in block_lines if line.strip())
            else:
                metadata[key] = "\n".join(line.rstrip() for line in block_lines)
            continue
        metadata[key] = value.strip('"').strip("'")

    problems: list[str] = []
    if not metadata.get("name"):
        problems.append("missing_name")
    if not metadata.get("description"):
        problems.append("missing_description")

    return metadata, problems


def keyword_matches(haystack: str, keyword: str) -> bool:
    pattern = rf"(?<![A-Za-z0-9]){re.escape(keyword)}(?![A-Za-z0-9])"
    return re.search(pattern, haystack, flags=re.IGNORECASE) is not None


def default_skill_roots() -> list[Path]:
    roots: list[Path] = []
    env_roots = os.environ.get("SKILL_ROUTE_ROOTS", "")
    for raw_root in env_roots.split(os.pathsep):
        if raw_root.strip():
            roots.append(Path(raw_root).expanduser())

    home = Path.home()
    roots.extend(
        [
            home / ".codex" / "skills",
            home / ".agents" / "skills",
            home / ".codex" / "skills" / ".system",
            home / ".codex" / "plugins" / "cache",
        ]
    )

    unique_roots: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        normalized = str(root.resolve()) if root.exists() else str(root)
        if normalized not in seen:
            seen.add(normalized)
            unique_roots.append(root)
    return unique_roots


def load_capability_groups(groups_file: Path | None) -> dict[str, list[str]]:
    if groups_file is None:
        default_file = Path(__file__).resolve().parents[1] / "references" / "capability-groups.json"
        groups_file = default_file

    if not groups_file.exists():
        return {}

    raw = json.loads(groups_file.read_text(encoding="utf-8"))
    groups: dict[str, list[str]] = {}
    for group, keywords in raw.items():
        groups[str(group)] = [str(keyword).lower() for keyword in keywords]
    return groups


def assign_capability_groups(record: SkillRecord, groups: dict[str, list[str]]) -> list[str]:
    haystack = " ".join([record.name, record.description])
    matches = [
        group
        for group, keywords in groups.items()
        if any(keyword_matches(haystack, keyword) for keyword in keywords)
    ]
    return matches or ["uncategorized"]


def scan_skill_roots(
    roots: Iterable[Path],
    visible_names: set[str] | None = None,
    capability_groups: dict[str, list[str]] | None = None,
) -> list[SkillRecord]:
    groups = capability_groups or {}
    visible = visible_names or set()
    records: list[SkillRecord] = []
    seen_skill_files: set[str] = set()

    for root in roots:
        root_path = Path(root).expanduser()
        if not root_path.exists():
            continue

        for skill_file in sorted(root_path.rglob("SKILL.md")):
            resolved_skill_file = str(skill_file.resolve())
            if resolved_skill_file in seen_skill_files:
                continue
            seen_skill_files.add(resolved_skill_file)

            metadata, problems = parse_frontmatter(skill_file)
            name = metadata.get("name", skill_file.parent.name)
            description = metadata.get("description", "")

            if problems:
                status = "invalid"
            elif visible_names is None:
                status = "installed"
            elif name in visible:
                status = "visible"
            else:
                status = "installed_not_visible"

            record = SkillRecord(
                name=name,
                description=description,
                path=str(skill_file),
                root=str(root_path),
                status=status,
                problems=problems,
            )
            record.capability_groups = assign_capability_groups(record, groups)
            records.append(record)

    name_counts = Counter(record.name for record in records if record.status != "invalid")
    duplicate_names = {name for name, count in name_counts.items() if count > 1}

    for record in records:
        if record.name in duplicate_names and record.status != "invalid":
            record.status = "duplicate"
            if "duplicate_name" not in record.problems:
                record.problems.append("duplicate_name")

    return records


def build_summary(records: list[SkillRecord]) -> dict[str, object]:
    status_counts = Counter(record.status for record in records)
    group_counts: Counter[str] = Counter()
    route_eligible_statuses = {"visible", "installed", "installed_not_visible"}

    for record in records:
        if record.status in route_eligible_statuses:
            group_counts.update(record.capability_groups)

    return {
        "total_records": len(records),
        "statuses": dict(sorted(status_counts.items())),
        "groups": dict(sorted(group_counts.items())),
    }


def parse_visible_names(raw_visible_names: str) -> set[str]:
    return {
        name.strip()
        for name in raw_visible_names.split(",")
        if name.strip()
    }


def build_payload(records: list[SkillRecord]) -> dict[str, object]:
    return {
        "summary": build_summary(records),
        "records": [record.to_dict() for record in records],
    }


def print_text_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    print("Skill scan summary")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print()
    print("Records")
    for record in payload["records"]:
        print(
            f"- {record['name']} [{record['status']}]: "
            f"{', '.join(record['capability_groups'])} :: {record['path']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan installed Codex skill files.")
    parser.add_argument("--roots", nargs="*", help="Skill roots to scan. Defaults to common user skill roots.")
    parser.add_argument("--visible-names", default="", help="Comma-separated skill names visible in the current session.")
    parser.add_argument("--groups", help="Path to capability group JSON.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    roots = [Path(root) for root in args.roots] if args.roots else default_skill_roots()
    visible_names = parse_visible_names(args.visible_names) if args.visible_names else None
    groups = load_capability_groups(Path(args.groups) if args.groups else None)

    records = scan_skill_roots(roots, visible_names=visible_names, capability_groups=groups)
    payload = build_payload(records)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print_text_summary(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
