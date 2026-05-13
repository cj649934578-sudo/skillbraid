import json
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[1]
REFERENCES_DIR = PACKAGE_DIR / "references"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_reference_json_files_parse():
    path = REFERENCES_DIR / "capability-groups.json"
    assert path.exists()
    payload = json.loads(read_text(path))
    assert isinstance(payload, dict)


def test_markdown_templates_define_route_storage_and_agents_index():
    skillbraid_template = read_text(REFERENCES_DIR / "SKILLBRAID.template.md")
    agents_template = read_text(REFERENCES_DIR / "AGENTS.skillbraid.md")

    assert "# SkillBraid Project Rules" in skillbraid_template
    assert "## Routes" in skillbraid_template
    assert "## Usage Notes" in skillbraid_template
    assert ".codex/skillbraid/SKILLBRAID.md" in agents_template
    assert "user-confirmed routes for recurring work" in agents_template
    assert "non-trivial task" in agents_template
    assert "Do not invent or force a route match." in agents_template
    assert "Do not create, update, or remove SkillBraid route rules unless the user confirms." in agents_template


def test_skill_frontmatter_and_required_phrasing():
    skill_file = PACKAGE_DIR / "SKILL.md"
    text = read_text(skill_file)

    assert text.splitlines()[0] == "---"
    assert "name: skillbraid" in text
    assert "description:" in text
    assert "本次链路：" in text
    assert "选择原因：" in text
    assert "后续可选优化：" in text
    assert ".codex\\skillbraid\\SKILLBRAID.md" in text
    assert "do not hardcode route triggers in `AGENTS.md`" in text
    assert "skillbraid:init" in text
    assert "skillbraid:update route <route-name>" in text
    assert "skillbraid:help" in text
    assert "Do not silently write or change route rules." in text
