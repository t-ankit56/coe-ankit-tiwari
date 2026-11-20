"""A DeepEval judge backed by Gemini. DeepEval's default judge is a paid OpenAI model."""
import os
from pathlib import Path

from deepeval.models import DeepEvalBaseLLM
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(Path(__file__).parent / ".env")

MODEL = "gemini-3.1-flash-lite"


class GeminiJudge(DeepEvalBaseLLM):
    def __init__(self):
        super().__init__(model=MODEL)

    def load_model(self):
        # attempts=1 means no automatic retry (the SDK default is 5, which would spend quota on failures)
        options = types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=1))
        return genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=options)

    def generate(self, prompt: str, schema=None):
        config = types.GenerateContentConfig(temperature=0.0, max_output_tokens=500)
        if schema is not None:
            config.response_mime_type = "application/json"
            config.response_schema = schema
        response = self.model.models.generate_content(model=MODEL, contents=prompt, config=config)
        return schema.model_validate_json(response.text) if schema is not None else response.text

    async def a_generate(self, prompt: str, schema=None):
        return self.generate(prompt, schema)

    def get_model_name(self) -> str:
        return MODEL
