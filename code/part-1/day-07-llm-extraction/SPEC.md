# LLM Extraction from Email and PDF: Spec

Build one Python function, `extract(source)`, that pulls named fields out of a short email or a PDF invoice using an LLM API and returns schema-valid data. This is for the Day 7 assessment. Testing is manual: results are checked by eye and recorded in the README. Automated evals come on Day 9.

## Provider

Google Gemini API, free tier. The key lives in an untracked `.env` (`GEMINI_API_KEY`), with a `.env.example` committed. The model ID and the PDF limits are taken from the current Gemini docs when the code is written.

## Criteria and how each is met

| Criterion | How |
| --- | --- |
| Calls an LLM API from Python with sensible settings | System prompt, low temperature, explicit `max_output_tokens`. The README says why each value was chosen. |
| Writes prompts for accuracy and consistency | Clear instructions, one worked example and a stated output format. |
| Gets schema-valid JSON with structured outputs | The Pydantic model is passed as the response schema, and the reply is validated against it. |
| Extracts fields from a PDF | `extract()` accepts a PDF path and sends the bytes to the model. |
| Handles missing or ambiguous input | A field that is absent or unclear comes back `None`. The model must never invent a value. |
| Measures the effect of a prompt change | Prompt v1 and v2 run on the same five emails, with the correct fields counted for each. |

## Design

- `extract(source)` takes email text, or a path to a `.pdf`, and returns an `Extraction`.
- One schema for both inputs, every field Optional: `sender`, `date`, `amount`, `reference`, `purpose`. For an invoice, `sender` is the vendor.
- Text goes to the model as a text part, a PDF as a PDF part. Everything else is shared.
- A malformed or schema-invalid reply raises a clear error. It is never silently repaired.
- The prompt text lives in its own module, `prompts.py`, with `v1` and `v2`, so a change is a visible diff.

## Samples

- Five made-up emails in `samples/emails/`, with no real names or data: a clean one, one with a field missing, one with an ambiguous field (such as "next Friday" or "about 500"), and two others of different kinds.
- One made-up invoice PDF in `samples/invoice.pdf`.
- Expected values for each are written in the README before the first run.

## Manual check

1. Run `extract()` on the five emails. Record expected, got and correct or not, per field.
2. Run it on the invoice. Check every field against the PDF.
3. Switch to prompt v2, run the same five emails, and record the before and after counts.

## Out of scope

pytest, fake clients and automated evals (Day 9), retries and rate-limit handling, multi-page or scanned PDFs, any real mailbox access.

## Commits

Small and incremental, in Conventional Commits style, so the history shows the build: spec, setup, email extraction, PDF input, samples and README, prompt v2, day file.
