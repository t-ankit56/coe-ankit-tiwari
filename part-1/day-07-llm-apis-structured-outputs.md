# Part 1 · Day 7 — LLM APIs, Prompting & Structured Outputs

**Date completed:** 2026-11-18 · **Time spent:**

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Calls an LLM API from Python with sensible settings | Yes | [extract.py](../code/part-1/day-07-llm-extraction/extract.py) · [settings and decisions](../code/part-1/day-07-llm-extraction/README.md#settings-and-decisions) |
| Writes prompts for accuracy and consistency | Yes | [prompts.py](../code/part-1/day-07-llm-extraction/prompts.py) · [v2 results](../code/part-1/day-07-llm-extraction/README.md#prompt-v2-one-complete-prompt) |
| Gets schema-valid JSON with structured outputs | Yes | [schema.py](../code/part-1/day-07-llm-extraction/schema.py) · [saved outputs](../code/part-1/day-07-llm-extraction/samples/outputs/) |
| Extracts fields from a PDF | Yes | [invoice results](../code/part-1/day-07-llm-extraction/README.md#invoice-results) · [PDF limits](../code/part-1/day-07-llm-extraction/README.md#pdf-limits) |
| Handles missing or ambiguous input | Yes | [02-missing](../code/part-1/day-07-llm-extraction/samples/emails/02-missing.txt) · [03-ambiguous](../code/part-1/day-07-llm-extraction/samples/emails/03-ambiguous.txt) · [07-date-format](../code/part-1/day-07-llm-extraction/samples/emails/07-date-format.txt) · [results](../code/part-1/day-07-llm-extraction/README.md#results) |
| Measures the effect of a prompt change | Yes | [v1 against v2](../code/part-1/day-07-llm-extraction/README.md#v1-against-v2) · [NOTES.md](../code/part-1/day-07-llm-extraction/NOTES.md) |

## Key learnings

- **Calling the API:** the system prompt sets the job, temperature 0 keeps extraction repeatable, and `max_output_tokens` caps a reply and its cost. The free tier's limits were unclear, so I saved every output and filled the tables from the files.
- **Structured outputs:** the Pydantic schema fixes the shape of the reply, not whether the values are right. Making every field Optional lets the model answer `None` instead of inventing something.
- **PDF:** the file is sent as it is, not as extracted text. The documented limit is 50 MB or 1,000 pages, at about 258 tokens a page.
- **Confidently wrong:** the bare prompt turned "about 500" into 500.0, and v2 guessed a company name from an email domain. What helped was defining each field, allowing `None`, and checking every result by hand against the source.

## Exercises

### Exercise 1: Extract named fields from an email into a validated schema

Spec: [SPEC.md](../code/part-1/day-07-llm-extraction/SPEC.md) · Code and decisions: [README](../code/part-1/day-07-llm-extraction/README.md) · Notes: [NOTES.md](../code/part-1/day-07-llm-extraction/NOTES.md)

One function, `extract(source)`, takes email text or a PDF path and returns an `Extraction` with six optional fields (sender, date, amount, currency, reference, purpose). It calls Gemini with a system prompt, temperature 0, a token cap and the schema as the response schema. Missing values come back as `None`.

### Exercise 2: Five emails, one with missing information

Ten made-up emails (the first five, three harder ones and two unseen ones), with expected values written before each run. Missing and ambiguous cases are `02-missing`, `03-ambiguous` and `07-date-format`. See the [results](../code/part-1/day-07-llm-extraction/README.md#results).

### Exercise 3: One PDF invoice checked against the document

Two invoices (simple and hard), each field checked against the PDF. See the [invoice results](../code/part-1/day-07-llm-extraction/README.md#invoice-results).

### Exercise 4: Change the prompt and measure

Prompt v1 (bare) against v2 (one complete prompt) on the same emails. See [v1 against v2](../code/part-1/day-07-llm-extraction/README.md#v1-against-v2).

v1 scored 56/60 on ten emails and v2 scored 59/60. v2 fixed the approximate amount, the wrong deadline, the raw ambiguous date and a purchase order number in `purpose`. It also added two misses: a guessed company name as sender, and the due date instead of the invoice date on both invoices. The two unseen emails scored 12/12 for both versions, so they showed no difference.

## Reflection

A lucky prompt gives a good answer on the example you tried. A reliable one is measured on several inputs, including the awkward ones, and checked against answers written down before the run. For me the weak spots were the cases the prompt did not describe: missing, vague or competing values. v2 got better by naming each field and saying what to do when a value is missing, but its date rule then clashed with the invoice rule on both invoices. So a prompt can look better on the cases it was written for and still break something else. I would not trust v2 without more samples that it was not written against.

## AI use

I used Claude Code (Sonnet 5.5) for this day. It wrote the code, the sample emails and invoices, the expected values, the v2 prompt text and the README tables. I approved each prompt and each batch of API calls before it ran. The marks that were judgement calls were Claude's first: `sender` in `08-european-format` and `date` in `05-two-amounts`. Claude also drafted the Key learnings, exercise summaries and Reflection from the results of this run. [Edit this paragraph to say what you checked and what you changed.]

## Open questions

- Would a v3 with a corrected date rule fix both invoices without breaking the emails?
- What are the real free-tier limits for this model? The documentation only points to the AI Studio page.
- v2 changed many things at once, so which of them did the work? Single-change versions would show it.
- How would scanned or multi-page PDFs behave? I only tried one-page invoices.

## Changes after review

- 
