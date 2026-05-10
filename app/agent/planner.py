def build_feature_plan(game_idea: str, game_type: str, scope: str, llm) -> str:
    return llm.generate_text(f"Build feature plan for {game_type}, scope={scope}, idea={game_idea}")
