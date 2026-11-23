"""A DeepEval judge backed by Gemini, and the correctness metric for the eval suite.

GeminiJudge is a deliberate copy of day-09-extraction-evals/judge.py, so Day 9 stays untouched.
DeepEval's default judge is a paid OpenAI model.
"""
import os

from deepeval.metrics import GEval
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import SingleTurnParams
from google import genai
from google.genai import types

MODEL = "gemini-3.1-flash-lite"
THRESHOLD = 0.7

# Written out so GEval does not spend a call generating them.
STEPS = [
    "The input is a question, the expected output is the correct answer, and the actual output is the service's answer.",
    "If the expected output is a fact, check that the actual output states the same fact. Different wording, units written out in words, or extra correct detail are fine.",
    "Penalise an actual output that gives a different number or value, or contradicts the expected fact.",
    "If the expected output says the answer is not in the documents, check that the actual output says it does not know or that the documents do not contain the answer. Penalise any answer given from outside knowledge.",
    "Ignore citation markers such as [1] or [2].",
]


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


def correctness_metric() -> GEval:
    return GEval(
        name="Correctness",
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
        evaluation_steps=STEPS,
        model=GeminiJudge(),
        threshold=THRESHOLD,
        async_mode=False,
    )
