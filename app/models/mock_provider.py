class MockLLMProvider:
    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        return f"[MOCK OUTPUT]\n{prompt[:600]}"
