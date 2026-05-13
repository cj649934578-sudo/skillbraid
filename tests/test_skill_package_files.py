import json
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[1]
REFERENCES_DIR = PACKAGE_DIR / "references"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_reference_json_files_parse():
    expected_files = [
        "capability-groups.json",
        "route-rules.schema.json",
        "route-rules.example.json",
        "usage-record.schema.json",
        "usage-record.example.json",
    ]

    for filename in expected_files:
        path = REFERENCES_DIR / filename
        assert path.exists(), f"Missing {filename}"
        payload = json.loads(read_text(path))
        assert isinstance(payload, dict)


def test_route_examples_match_declared_version_and_scope():
    route_example = json.loads(read_text(REFERENCES_DIR / "route-rules.example.json"))
    usage_example = json.loads(read_text(REFERENCES_DIR / "usage-record.example.json"))

    assert route_example["version"] == "1.0"
    assert route_example["scope"] == "project"
    assert route_example["routes"][0]["chain"][0]["skill"] == "brainstorming"
    assert usage_example["version"] == "1.0"
    assert usage_example["records"][0]["route_name"] == "skill-creation-maintenance"


def test_skill_frontmatter_and_required_phrasing():
    skill_file = PACKAGE_DIR / "SKILL.md"
    text = read_text(skill_file)

    assert text.splitlines()[0] == "---"
    assert "name: skillbraid" in text
    assert "description:" in text
    assert "本次链路：" in text
    assert "选择原因：" in text
    assert "后续可选优化：" in text
    assert "Do not silently write or change route rules." in text
