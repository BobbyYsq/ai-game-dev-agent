def generate_review_report(project_name: str, generated_files: list[str], llm) -> str:
    return llm.generate_text(f"Review {project_name}, files: {', '.join(generated_files)}")
