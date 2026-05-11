class MockLLMProvider:
    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        if "Allowed operation values:" in prompt and "Return only JSON" in prompt:
            return (
                '{"operations": ['
                '{"operation": "open_scene", "target_scene": "res://scenes/Main.tscn"}, '
                '{"operation": "create_node", "node_type": "Node2D", "node_name": "AgentGeneratedNode", "parent_path": "."}, '
                '{"operation": "save_scene"}'
                "]}"
            )
        return f"[MOCK OUTPUT]\n{prompt[:600]}"
