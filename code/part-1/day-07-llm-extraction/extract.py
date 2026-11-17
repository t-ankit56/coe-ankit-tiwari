import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import PROMPTS
from schema import Extraction

MODEL = "gemini-3.1-flash-lite"
TEMPERATURE = 0.0
MAX_OUTPUT_TOKENS = 500


def extract(source: str, prompt_version: str = "v1") -> Extraction:
    """Extract the fields from email text. Raises ValueError on a bad reply."""
    load_dotenv()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model=MODEL,
        contents=source,
        config=types.GenerateContentConfig(
            system_instruction=PROMPTS[prompt_version],
            temperature=TEMPERATURE,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            response_mime_type="application/json",
            response_schema=Extraction,
        ),
    )

    try:
        return Extraction.model_validate_json(response.text)
    except Exception as error:
        raise ValueError(f"Model reply is not a valid Extraction: {response.text!r}") from error


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--prompt", default="v1")
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as f:
        text = f.read()
    print(extract(text, args.prompt).model_dump_json(indent=2))
