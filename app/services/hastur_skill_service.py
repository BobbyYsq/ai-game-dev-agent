from __future__ import annotations

from dataclasses import dataclass, field
import base64
import io
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from app.config import HASTUR_SKILLS_DIR, USER_SKILLS_DIR
from app.services.asset_service import get_project_dir


SKILL_SCOPES = {"vendored", "global", "project"}
USER_WRITABLE_SCOPES = {"global", "project"}
MAX_UPLOAD_BYTES = 2_000_000
MAX_UPLOAD_FILES = 80
MAX_DESCRIPTION_CHARS = 1536
ALLOWED_SKILL_EXTENSIONS = {
    ".cfg",
    ".css",
    ".csv",
    ".gd",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".svg",
    ".toml",
    ".ts",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


@dataclass
class HasturSkill:
    name: str
    description: str
    path: str
    scope: str = "vendored"
    readonly: bool = True
    path_label: str = ""
    when_to_use: str = ""
    argument_hint: str = ""
    arguments: list[str] = field(default_factory=list)
    disable_model_invocation: bool = False
    user_invocable: bool = True
    allowed_tools: list[str] = field(default_factory=list)
    model: str = ""
    effort: str = ""
    context: str = ""
    paths: list[str] = field(default_factory=list)


def list_hastur_skills(project_slug: str | None = None) -> list[HasturSkill]:
    skills: list[HasturSkill] = []
    for scope, root, readonly in _skill_roots(project_slug):
        if not root.exists():
            continue
        for path in sorted(root.iterdir()):
            skill = _skill_from_dir(path, scope, readonly, root)
            if skill:
                skills.append(skill)
    return skills


def skill_listing_for_prompt(project_slug: str | None = None) -> str:
    items = []
    for skill in list_hastur_skills(project_slug):
        if skill.disable_model_invocation:
            continue
        when = f" when_to_use={_clip(skill.when_to_use, 300)!r}" if skill.when_to_use else ""
        flags = []
        if not skill.user_invocable:
            flags.append("model-only")
        if skill.paths:
            flags.append(f"paths={','.join(skill.paths[:4])}")
        flag_text = f" flags={','.join(flags)}" if flags else ""
        items.append(
            f"- /{skill.name} ({skill.scope}) description={_clip(skill.description, 500)!r}{when}{flag_text}"
        )
    return "\n".join(items) or "- No skills discovered."


def load_hastur_skill(skill_name: str, project_slug: str | None = None) -> str:
    skill = get_skill_metadata(skill_name, project_slug=project_slug)
    return Path(skill.path).read_text(encoding="utf-8", errors="replace")


def get_skill_metadata(skill_name: str, project_slug: str | None = None, scope: str | None = None) -> HasturSkill:
    requested_scope, requested_name = _split_scoped_name(skill_name)
    if scope:
        requested_scope = scope
    safe_name = _validate_skill_lookup_name(requested_name)
    skills = list_hastur_skills(project_slug)
    if not requested_scope:
        scope_rank = {"project": 0, "global": 1, "vendored": 2}
        skills = sorted(skills, key=lambda item: scope_rank.get(item.scope, 99))
    for skill in skills:
        if requested_scope and skill.scope != requested_scope:
            continue
        if skill.name == safe_name:
            return skill
    raise FileNotFoundError(f"Hastur skill not found: {skill_name}")


def delete_skill(scope: str, skill_name: str, project_slug: str | None = None) -> dict[str, Any]:
    if scope not in USER_WRITABLE_SCOPES:
        raise ValueError("Only global and project skills can be deleted.")
    skill = get_skill_metadata(skill_name, project_slug=project_slug, scope=scope)
    if skill.readonly:
        raise ValueError("This skill is read-only.")
    root = _root_for_scope(scope, project_slug)
    target = Path(skill.path).parent.resolve()
    root_resolved = root.resolve()
    if root_resolved not in [target, *target.parents]:
        raise ValueError("Skill path is outside the writable skills directory.")
    shutil.rmtree(target)
    return {"success": True, "message": f"Deleted {scope} skill {skill.name}.", "skill": skill.name}


def upload_skill(scope: str, files: list[dict[str, str]], project_slug: str | None = None) -> dict[str, Any]:
    if scope not in USER_WRITABLE_SCOPES:
        raise ValueError("Upload scope must be global or project.")
    if not files:
        raise ValueError("Upload at least one skill file.")
    if len(files) > MAX_UPLOAD_FILES:
        raise ValueError(f"Upload too many files; limit is {MAX_UPLOAD_FILES}.")
    decoded = [_decode_upload_file(item) for item in files]
    total_size = sum(len(data) for _, data in decoded)
    if total_size > MAX_UPLOAD_BYTES:
        raise ValueError(f"Skill upload is too large; limit is {MAX_UPLOAD_BYTES} bytes.")
    root = _root_for_scope(scope, project_slug)
    root.mkdir(parents=True, exist_ok=True)
    if len(decoded) == 1 and decoded[0][0].suffix.lower() == ".zip":
        return _install_zip_skill(root, scope, decoded[0][1], project_slug)
    return _install_file_skill(root, scope, decoded, project_slug)


def _skill_roots(project_slug: str | None) -> list[tuple[str, Path, bool]]:
    roots = [("vendored", HASTUR_SKILLS_DIR, True), ("global", USER_SKILLS_DIR, False)]
    if project_slug:
        try:
            roots.append(("project", get_project_dir(project_slug) / ".claude" / "skills", False))
        except FileNotFoundError:
            pass
    return roots


def _root_for_scope(scope: str, project_slug: str | None = None) -> Path:
    if scope == "global":
        return USER_SKILLS_DIR
    if scope == "project":
        if not project_slug:
            raise ValueError("project_slug is required for project skills.")
        return get_project_dir(project_slug) / ".claude" / "skills"
    if scope == "vendored":
        return HASTUR_SKILLS_DIR
    raise ValueError(f"Unknown skill scope: {scope}")


def _skill_from_dir(path: Path, scope: str, readonly: bool, root: Path) -> HasturSkill | None:
    skill_file = path / "SKILL.md"
    if not path.is_dir() or not skill_file.exists():
        return None
    text = skill_file.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = _parse_frontmatter(text)
    name = _skill_name(frontmatter.get("name"), path.name)
    description = str(frontmatter.get("description") or _first_paragraph(body)).strip()
    when_to_use = str(frontmatter.get("when_to_use") or "").strip()
    return HasturSkill(
        name=name,
        description=_clip(" ".join([description, when_to_use]).strip(), MAX_DESCRIPTION_CHARS),
        path=str(skill_file),
        scope=scope,
        readonly=readonly,
        path_label=_path_label(skill_file, root),
        when_to_use=_clip(when_to_use, MAX_DESCRIPTION_CHARS),
        argument_hint=str(frontmatter.get("argument-hint") or frontmatter.get("argument_hint") or "").strip(),
        arguments=_as_list(frontmatter.get("arguments")),
        disable_model_invocation=_as_bool(frontmatter.get("disable-model-invocation", frontmatter.get("disable_model_invocation", False))),
        user_invocable=_as_bool(frontmatter.get("user-invocable", frontmatter.get("user_invocable", True))),
        allowed_tools=_as_list(frontmatter.get("allowed-tools", frontmatter.get("allowed_tools"))),
        model=str(frontmatter.get("model") or "").strip(),
        effort=str(frontmatter.get("effort") or "").strip(),
        context=str(frontmatter.get("context") or "").strip(),
        paths=_as_list(frontmatter.get("paths")),
    )


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end_index = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if end_index is None:
        return {}, text
    frontmatter_lines = lines[1:end_index]
    body = "\n".join(lines[end_index + 1 :])
    values: dict[str, Any] = {}
    index = 0
    while index < len(frontmatter_lines):
        line = frontmatter_lines[index]
        if not line.strip() or line.startswith((" ", "\t")) or ":" not in line:
            index += 1
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value in {"|", ">"}:
            index += 1
            block: list[str] = []
            while index < len(frontmatter_lines):
                next_line = frontmatter_lines[index]
                if next_line and not next_line.startswith((" ", "\t")) and ":" in next_line:
                    break
                block.append(next_line[2:] if next_line.startswith("  ") else next_line.strip())
                index += 1
            values[key] = "\n".join(block).strip() if value == "|" else " ".join(part.strip() for part in block).strip()
            continue
        if value == "":
            index += 1
            block_items: list[str] = []
            while index < len(frontmatter_lines):
                next_line = frontmatter_lines[index]
                stripped = next_line.strip()
                if next_line and not next_line.startswith((" ", "\t")) and ":" in next_line:
                    break
                if stripped.startswith("- "):
                    block_items.append(_strip_quotes(stripped[2:].strip()))
                index += 1
            values[key] = block_items
            continue
        values[key] = _parse_scalar(value)
        index += 1
    return values, body


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        return [_strip_quotes(part.strip()) for part in body.split(",") if part.strip()]
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    return _strip_quotes(value)


def _strip_quotes(value: str) -> str:
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def _first_paragraph(text: str) -> str:
    paragraphs = [part.strip() for part in text.strip().split("\n\n") if part.strip()]
    return paragraphs[0] if paragraphs else ""


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if "," in text:
        return [part.strip() for part in text.split(",") if part.strip()]
    return [part.strip() for part in text.split() if part.strip()]


def _skill_name(raw_name: Any, fallback: str) -> str:
    candidate = str(raw_name or fallback).strip()
    if _valid_skill_name(candidate):
        return candidate
    slug = re.sub(r"[^a-z0-9-]+", "-", candidate.lower()).strip("-")
    return slug[:64] if _valid_skill_name(slug) else fallback


def _valid_skill_name(value: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value))


def _validate_skill_lookup_name(value: str) -> str:
    if not _valid_skill_name(value):
        raise FileNotFoundError(f"Invalid skill name: {value}")
    return value


def _split_scoped_name(value: str) -> tuple[str, str]:
    name = value.strip()
    if ":" in name:
        scope, rest = name.split(":", 1)
        if scope in SKILL_SCOPES:
            return scope, rest
    return "", name


def _path_label(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return path.name


def _clip(value: str, limit: int) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def _decode_upload_file(item: dict[str, str]) -> tuple[Path, bytes]:
    raw_name = item.get("relative_path") or item.get("filename") or ""
    rel_path = _safe_relative_path(raw_name)
    payload = str(item.get("data") or "")
    if "," in payload and payload.split(",", 1)[0].endswith(";base64"):
        payload = payload.split(",", 1)[1]
    try:
        data = base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise ValueError(f"Invalid base64 data for {raw_name}.") from exc
    if rel_path.suffix.lower() != ".zip":
        _validate_skill_member(rel_path, len(data))
    return rel_path, data


def _safe_relative_path(value: str) -> Path:
    normalized = value.replace("\\", "/").strip("/")
    if not normalized:
        raise ValueError("Uploaded file is missing a filename.")
    path = Path(normalized)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Invalid skill upload path: {value}")
    return path


def _validate_skill_member(path: Path, size: int) -> None:
    if path.name.startswith(".") and path.name != ".gdignore":
        raise ValueError(f"Hidden skill files are not allowed: {path}")
    if path.suffix.lower() not in ALLOWED_SKILL_EXTENSIONS:
        raise ValueError(f"Unsupported skill file type: {path.suffix or path.name}")
    if size > MAX_UPLOAD_BYTES:
        raise ValueError(f"Skill file is too large: {path}")


def _install_zip_skill(root: Path, scope: str, data: bytes, project_slug: str | None) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = [member for member in archive.infolist() if not member.is_dir()]
        if len(members) > MAX_UPLOAD_FILES:
            raise ValueError(f"Zip contains too many files; limit is {MAX_UPLOAD_FILES}.")
        total = sum(member.file_size for member in members)
        if total > MAX_UPLOAD_BYTES:
            raise ValueError(f"Zip contents are too large; limit is {MAX_UPLOAD_BYTES} bytes.")
        safe_members: list[tuple[Path, zipfile.ZipInfo]] = []
        for member in members:
            rel_path = _safe_relative_path(member.filename)
            _validate_skill_member(rel_path, member.file_size)
            safe_members.append((rel_path, member))
        skill_roots = {path.parent for path, _ in safe_members if path.name == "SKILL.md"}
        if len(skill_roots) != 1:
            raise ValueError("A skill zip must contain exactly one SKILL.md.")
        skill_root = next(iter(skill_roots))
        skill_text = archive.read(next(member for path, member in safe_members if path.name == "SKILL.md")).decode("utf-8", errors="replace")
        name = _skill_name(_parse_frontmatter(skill_text)[0].get("name"), skill_root.name or "uploaded-skill")
        destination = _reserve_skill_destination(root, name)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            for rel_path, member in safe_members:
                output_rel = rel_path.relative_to(skill_root) if skill_root.parts else rel_path
                output = tmp_root / output_rel
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(archive.read(member))
            shutil.copytree(tmp_root, destination)
    skill = get_skill_metadata(name, project_slug=project_slug, scope=scope)
    return {"success": True, "message": f"Uploaded {scope} skill {name}.", "skill": skill.__dict__}


def _install_file_skill(root: Path, scope: str, files: list[tuple[Path, bytes]], project_slug: str | None) -> dict[str, Any]:
    skill_paths = [path for path, _ in files if path.name == "SKILL.md"]
    if len(skill_paths) != 1:
        raise ValueError("Upload must include exactly one SKILL.md.")
    skill_root = skill_paths[0].parent
    skill_data = next(data for path, data in files if path == skill_paths[0])
    skill_text = skill_data.decode("utf-8", errors="replace")
    name = _skill_name(_parse_frontmatter(skill_text)[0].get("name"), skill_root.name or "uploaded-skill")
    destination = _reserve_skill_destination(root, name)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        for rel_path, data in files:
            if skill_root.parts:
                try:
                    output_rel = rel_path.relative_to(skill_root)
                except ValueError as exc:
                    raise ValueError("All uploaded skill files must live under the SKILL.md folder.") from exc
            else:
                output_rel = rel_path
            output = tmp_root / output_rel
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)
        shutil.copytree(tmp_root, destination)
    skill = get_skill_metadata(name, project_slug=project_slug, scope=scope)
    return {"success": True, "message": f"Uploaded {scope} skill {name}.", "skill": skill.__dict__}


def _reserve_skill_destination(root: Path, name: str) -> Path:
    if not _valid_skill_name(name):
        raise ValueError(f"Invalid skill name: {name}")
    root.mkdir(parents=True, exist_ok=True)
    destination = root / name
    if destination.exists():
        raise ValueError(f"Skill already exists: {name}")
    return destination
