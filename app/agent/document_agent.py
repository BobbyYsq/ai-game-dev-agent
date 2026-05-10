def generate_gdd(project_name: str, game_idea: str, llm) -> str:
    return llm.generate_text(f"Write GDD for {project_name}: {game_idea}")

def generate_tech_design(project_name: str, game_type: str, llm) -> str:
    return llm.generate_text(f"Write technical design for {project_name}, type {game_type}")

def generate_asset_list(project_name: str, game_idea: str, llm) -> str:
    return llm.generate_text(f"Write asset list for {project_name}: {game_idea}")
