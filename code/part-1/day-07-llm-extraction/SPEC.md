# LLM Extraction from Email and PDF in Python: Build Spec for Claude Code

Build one function, `extract(source)`, that pulls named fields out of a short email or a PDF invoice using the Gemini API and returns schema-valid data, in Python. Then improve the prompt step by step and measure each change. This is for the Day 7 assessment, so the prompt history, the recorded results and the commit history matter as much as the final code. Testing is manual (no pytest). Automated evals come on Day 9.

## Instructions for Claude Code

**Ground rules**

1. **Always use plan mode.** Before every step, enter plan mode. The plan names what you will write and which calls you will make. Write no files and make no API calls until the user approves the plan.
2. **Never commit.** Do not run `git add`, `git commit` or any other git command that changes state. Read-only commands such as `git status` and `git diff` are fine. The user makes every commit. After each step, give a suggested commit message, then wait.
3. **One step at a time.** Stop after each step, show what changed and the suggested commit message, then wait for the user to say continue. The user wants to understand each step, not just receive the result.
4. **Keep API calls to a minimum.** The free-tier limits could not be confirmed (per-model figures are only shown in AI Studio). Every call must be named in the step's plan and approved. Never loop, never retry automatically, never re-run to see if the answer changes. Save every output to a file and fill the README from the saved files.
5. **Never print or commit the key.** `GEMINI_API_KEY` is read from `.env` (gitignored). Do not echo it, log it, or put it in the README, `NOTES.md` or the day file. Only `.env.example` with a placeholder is committed.
6. **No tests.** Do not add pytest, a fake client or an eval script. Checking is manual: expected against got, recorded in the README.
7. **Do not "fix" v1.** The first prompt is deliberately weak so there is something to improve. Change one thing per version, never several at once, and never edit an old version. Add a new one.
8. **Never invent data.** The samples are made up, with no real names, emails or amounts. No real mailbox is read.
9. **Simplest real thing first.** Dependencies are `google-genai`, `pydantic` and `python-dotenv` only. No frameworks, no retries, no caching layer.
10. **Keep notes.** Whenever a prompt change moves a score, append one line to `NOTES.md`. The user will use these for the reflection.
11. **Reflection and AI use are the user's.** Do not write them in the day file.

## Provider and model

Google Gemini API, free tier. The model is one constant at the top of `extract.py`: `gemini-3.1-flash-lite` (chosen from the key's model list: Flash-Lite class, no preview tag). The fallbacks are `gemini-2.5-flash-lite`, then `gemini-2.5-flash`. Do not use the `-latest` aliases, because a model that changes between runs would spoil the prompt comparison.

## Scope

- `extract(source)`: takes email text or a path ending in `.pdf`, returns an `Extraction`
- An `Extraction` Pydantic model with every field Optional
- `prompts.py` with one entry per prompt version
- Five made-up emails, one made-up invoice PDF, and saved outputs for every run
- A way to run it from the command line: `python extract.py <file> [--prompt v2]`

## Design

`extract` decides the input type, builds the request, calls the model once, and validates the reply. It uses a low temperature, an explicit `max_output_tokens`, a system instruction from the chosen prompt version, and the Pydantic model as the response schema.

| Piece | Job |
| --- | --- |
| `Extraction` | `sender`, `date`, `amount`, `currency`, `reference`, `purpose`. All `None` by default. For an invoice, `sender` is the vendor. |
| `PROMPTS` | A dict of version name to system prompt text: `v1`, `v2`, and so on. |
| `extract` | Text goes to the model as a text part, a PDF as a PDF part. Everything else is shared. Raises a clear error on an API failure, or on a reply that is not valid JSON or fails the schema. It never repairs a reply silently. |
| `__main__` | Reads the file from the command line, picks the prompt version, prints the result as JSON. Redirecting stdout saves it. |

Missing or unclear information must come back as `None`. The schema allows it, and from v3 onward the prompt says so.

## Folder layout

```
code/part-1/day-07-llm-extraction/
  requirements.txt
  .env.example        # placeholder only; .env is gitignored
  README.md
  NOTES.md
  SPEC.md
  extract.py          # MODEL constant, extract(), command-line entry
  schema.py           # Extraction
  prompts.py          # PROMPTS: v1, v2, ...
  samples/
    emails/           # five made-up emails (.txt)
    invoice.pdf       # one made-up invoice
    outputs/
      v1/ v2/ ...     # saved JSON per prompt version, plus invoice.json
```

Python files are flat because the project is small. The schema and prompts are split out so a prompt change is a visible diff and nothing else moves. The `venv/` folder and `.env` are already gitignored at the repo root.

## Step 0: Project setup

Do this first. No API calls yet.

1. Create the `venv/`, activate it, and install `google-genai`, `pydantic` and `python-dotenv`. Freeze to `requirements.txt`.
2. Confirm `.env` exists, is gitignored, and `.env.example` has a placeholder. (Already done. Verify with `git check-ignore`.)
3. Create empty `NOTES.md`, `README.md`, `samples/emails/`, and `samples/outputs/`.
4. Check the install imports cleanly: `python -c "import google.genai, pydantic"`.

**Suggested commit message:** `chore: project setup with requirements and env example`

## The samples

Write these before any API call, with the expected values recorded in the README first, so the answers cannot be fitted to the output.

| File | Kind | What it tests |
| --- | --- | --- |
| `01-clean.txt` | Everything stated clearly | The easy case |
| `02-missing.txt` | No date and no amount | The field must be `None`, not invented |
| `03-ambiguous.txt` | "next Friday", "about 500" | A vague value must not become a precise one |
| `04-*.txt` | A different kind of email (such as a meeting request) | Prompt works beyond one type |
| `05-*.txt` | Two amounts or two dates in one email | Choosing the right one |
| `invoice.pdf` | One-page made-up invoice | The PDF path, all fields checkable against the page |

## The steps

### Step 1: the schema and email extraction with prompt v1

1. `schema.py`: the `Extraction` model.
2. `prompts.py`: `v1` is bare, for example "Extract the information from this email."
3. `extract.py`: the `MODEL` constant, `extract()` for text only, and the command-line entry. Low temperature, explicit `max_output_tokens`, the schema as the response schema.
4. **One live call**, on `01-clean.txt`. Confirm the reply parses into `Extraction`.

**Suggested commit messages:** `feat: Extraction schema and prompt v1`, then `feat: extract email text with structured output`

### Step 2: PDF input

1. Extend `extract()`: a path ending in `.pdf` is read as bytes and sent as a PDF part. Check the Gemini docs for the part format (inline data, 50 MB or 1,000 pages is the documented limit).
2. A missing file raises a clear error before any API call.
3. **One live call**, on `invoice.pdf` with v1.

**Suggested commit message:** `feat: extract fields from a PDF`

### Step 3: samples and expected values

1. Write the five emails and the invoice (the invoice can be made with any tool, with no private data).
2. In `README.md`, write the expected value of every field for every sample, in a table, before running anything else.
3. No API calls.

**Suggested commit message:** `docs: sample emails, invoice and expected values`

### Step 4: baseline run with v1

1. Run the five emails once each with v1, saving to `samples/outputs/v1/`. Pause between calls.
2. In the README, add a table of expected, got and correct per field, and a score such as "14 of 25 fields correct".
3. Note in `NOTES.md` which failures stand out (invented values, wrong field, wrong format).

**Suggested commit message:** `docs: baseline results for prompt v1`

### Step 5: improve the prompt, one change per version

Each version is its own pass of the same four actions: add the new entry in `prompts.py`, run the five emails once with it, save to `samples/outputs/<version>/`, and add a column to the README table. Stop after each version.

| Version | One change | What it should fix |
| --- | --- | --- |
| `v2` | Define each field (what `sender`, `reference`, `purpose` mean, the date format, the amount as a number) | Wrong or inconsistent fields |
| `v3` | Add "use null when a value is not stated; never guess" | Invented values on the missing and ambiguous emails |
| `v4` | Add one worked example (input and expected output) | Remaining format and choice errors |

If a version scores worse or no better, keep it in the table and say so. Do not remove it. If v1 already scores full marks, say that plainly in the README and add a harder email rather than faking a gap.

**Suggested commit messages:** `feat: prompt v2 with field definitions`, `feat: prompt v3 with null for missing values`, `feat: prompt v4 with a worked example`, each followed by `docs: results for prompt vN`

### Step 6: the invoice with the best prompt

1. Run `invoice.pdf` once with the best-scoring version, saving to `samples/outputs/invoice.json`.
2. In the README, add a field-by-field table of the PDF's value, the extracted value and correct or not.
3. Note the PDF limits from the docs.

**Suggested commit message:** `docs: invoice extraction checked against the PDF`

## Decisions

Fill this table in the README once the code is written. Starting questions:

| Question | Decision |
| --- | --- |
| Why a low temperature? | Extraction wants the same answer for the same input, not variety. |
| Why `max_output_tokens`? | The output is a few fields. A cap stops a runaway reply and limits cost. |
| Why structured output and not "reply in JSON"? | The schema constrains the reply and gives a validation point. A prompt alone can be ignored. |
| Why is every field Optional? | The input may not contain the value. `None` is a correct answer, and a required field would push the model to invent one. |
| Why one function for text and PDF? | The task is the same extraction. Only the input part differs. |
| Why a Flash-Lite model? | Cheapest and most generous on quota, and enough for extraction. |
| Why pin the model and avoid `-latest`? | A changing model would make the prompt comparison meaningless. |
| Why save every output? | So the README is filled from files, with no repeat calls against a limited quota. |
| Why no retries? | A retry loop burns the quota fastest. A failed call raises an error. |

## Final step: README, manual check and verification

Write `README.md` with these parts:

1. What it is and how to run it (`pip install -r requirements.txt`, `python extract.py <file> --prompt v3`).
2. The settings chosen and why (the Decisions above).
3. The expected-values table, the per-version results, and the invoice table.
4. The PDF limits and the free-tier note, with the model ID used.

The Key learnings, the reflection and the AI use section go in `part-1/day-07-llm-apis-structured-outputs.md`, in the user's own words. Add the Day 7 row to the root `README.md`.

**Before finishing, verify each success criterion**

| Criterion | Where it shows |
| --- | --- |
| Calls an LLM API from Python with sensible settings | `extract()` sets a system prompt, a low temperature and `max_output_tokens`; the README explains each |
| Writes prompts for accuracy and consistency | `prompts.py` holds the versions, and the README table shows the effect of each |
| Gets schema-valid JSON with structured outputs | The `Extraction` model is the response schema and the reply is validated against it |
| Extracts fields from a PDF | `extract("samples/invoice.pdf")` and the invoice table in the README |
| Handles missing or ambiguous input | Samples 02 and 03 return `None` or a hedged value, not an invented one (from v3 onward) |
| Measures the effect of a prompt change | The README table, one column per version, on the same five emails |

Finally, confirm `git status` shows no `.env` and `git diff` contains no key, then suggest the commit message `docs: README and notes`. The user commits.
