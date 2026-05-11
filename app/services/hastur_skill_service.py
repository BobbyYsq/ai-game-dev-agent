from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from app.config import HASTUR_SKILLS_DIR


@dataclass
class HasturSkill:
    name: str
    description: str
    path: str


def list_hastur_skills() -> list[HasturSkill]:
    if not HASTUR_SKILLS_DIR.exists():
        return []
    skills = []
    for path in sorted(HASTUR_SKILLS_DIR.iterdir()):
        skill_file = path / "SKILL.md"
        if not path.is_dir() or not skill_file.exists():
            continue
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        name = _frontmatter_value(text, "name") or path.name
        description = _frontmatter_value(text, "description") or _first_paragraph(text)
        skills.append(HasturSkill(name=name, description=description.strip(), path=str(skill_file)))
    return skills


def load_hastur_skill(skill_name: str) -> str:
    safe_name = skill_name.strip()
    if not safe_name or any(part in safe_name for part in ["..", "/", "\\"]):
        raise FileNotFoundError(f"Invalid skill name: {skill_name}")
    path = HASTUR_SKILLS_DIR / safe_name / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"Hastur skill not found: {skill_name}")
    return path.read_text(encoding="utf-8", errors="replace")


def _frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip()
    if value == "|":
        block = re.search(rf"^{re.escape(key)}:\s*\|\s*\n(?P<body>(?:  .+\n?)+)", text, re.MULTILINE)
        if block:
            return " ".join(line.strip() for line in block.group("body").splitlines())
    return value.strip("\"'")


def _first_paragraph(text: str) -> str:
    body = re.sub(r"^---.*?---", "", text, flags=re.DOTALL).strip()
    paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
    return paragraphs[0] if paragraphs else ""
