from dataclasses import dataclass
from pathlib import Path
import re

from app.agent.document_agent import generate_asset_list, generate_gdd, generate_tech_design
from app.agent.godot_agent import generate_godot_project
from app.agent.planner import build_feature_plan
from app.agent.review_agent import generate_review_report
from app.config import GENERATED_PROJECTS_DIR
from app.models.llm_provider import get_llm_provider
from app.services.git_service import commit_all, init_repo
from app.services.settings_service import load_private_settings
from app.tools.godot_templates.base import write_godot_project_notes

@dataclass
class CreateProjectResult:
    success: bool
    project_slug: str
    project_path: str
    generated_files: list[str]
    review_summary: str
    next_steps: list[str]
    project_template: str

def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "project"

def create_ai_game_project(request) -> CreateProjectResult:
    llm = get_llm_provider()
    slug = slugify(request.project_name)
    pdir = GENERATED_PROJECTS_DIR / slug
    pdir.mkdir(parents=True, exist_ok=True)
    docs_dir = pdir / "docs"
    generated = []
    if request.generate_docs:
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir/"GDD.md").write_text(generate_gdd(request.project_name, request.game_idea, llm), encoding='utf-8')
        (docs_dir/"TECH_DESIGN.md").write_text(generate_tech_design(request.project_name, request.game_type, llm), encoding='utf-8')
        (docs_dir/"FEATURE_TASKS.md").write_text(build_feature_plan(request.game_idea, request.game_type, request.prototype_scope, llm), encoding='utf-8')
        (docs_dir/"ASSET_LIST.md").write_text(generate_asset_list(request.project_name, request.game_idea, llm), encoding='utf-8')
        generated += [f"docs/{n}" for n in ["GDD.md","TECH_DESIGN.md","FEATURE_TASKS.md","ASSET_LIST.md"]]
    if request.generate_godot_skeleton:
        settings = load_private_settings()
        broker_host = str(settings.get("hastur_broker_host", "localhost"))
        broker_port = int(settings.get("hastur_broker_tcp_port", 5301))
        for fp in generate_godot_project(pdir, request.project_name, request.game_type, request.project_template, broker_host, broker_port):
            generated.append(fp.relative_to(pdir).as_posix())
        notes_path = write_godot_project_notes(pdir, request.engine, broker_host, broker_port)
        generated.append(notes_path.relative_to(pdir).as_posix())
    review = generate_review_report(request.project_name, generated, llm)
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir/"REVIEW_REPORT.md").write_text(review, encoding='utf-8')
    generated.append("docs/REVIEW_REPORT.md")
    if request.enable_git:
        try:
            init_repo(pdir); commit_all(pdir, "Initial AI-generated project scaffold")
        except Exception:
            pass
    return CreateProjectResult(True, slug, str(pdir), sorted(set(generated)), "Created a playable Godot prototype.", ["Open project in Godot 4.", "Review docs/GDD.md.", "Run Main scene."], request.project_template)
