from openai import OpenAI


class OpenAIProvider:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("OpenAI API key is not configured.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(model=self.model, messages=messages)
        return resp.choices[0].message.content or ""
