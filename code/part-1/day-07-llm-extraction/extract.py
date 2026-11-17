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


def build_contents(source: str):
    """A path ending in .pdf is sent as a PDF part; anything else is email text."""
    if source.lower().endswith(".pdf"):
        if not os.path.isfile(source):
            raise FileNotFoundError(f"PDF not found: {source}")
        with open(source, "rb") as f:
            return types.Part.from_bytes(data=f.read(), mime_type="application/pdf")
    return source


def extract(source: str, prompt_version: str = "v1") -> Extraction:
    """Extract the fields from email text or a PDF path. Raises ValueError on a bad reply."""
    contents = build_contents(source)  # fails before any API call if the file is missing
    load_dotenv()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
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

    if args.file.lower().endswith(".pdf"):
        source = args.file
    else:
        with open(args.file, encoding="utf-8") as f:
            source = f.read()
    print(extract(source, args.prompt).model_dump_json(indent=2))
