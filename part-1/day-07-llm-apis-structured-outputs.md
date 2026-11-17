# Part 1 · Day 7 — LLM APIs, Prompting & Structured Outputs

**Date completed:** 2026-11-18 · **Time spent:**

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Calls an LLM API from Python with sensible settings | | [extract.py](../code/part-1/day-07-llm-extraction/extract.py) · [settings and decisions](../code/part-1/day-07-llm-extraction/README.md#settings-and-decisions) |
| Writes prompts for accuracy and consistency | | [prompts.py](../code/part-1/day-07-llm-extraction/prompts.py) · [v2 results](../code/part-1/day-07-llm-extraction/README.md#prompt-v2-one-complete-prompt) |
| Gets schema-valid JSON with structured outputs | | [schema.py](../code/part-1/day-07-llm-extraction/schema.py) · [saved outputs](../code/part-1/day-07-llm-extraction/samples/outputs/) |
| Extracts fields from a PDF | | [invoice results](../code/part-1/day-07-llm-extraction/README.md#invoice-results) · [PDF limits](../code/part-1/day-07-llm-extraction/README.md#pdf-limits) |
| Handles missing or ambiguous input | | [02-missing](../code/part-1/day-07-llm-extraction/samples/emails/02-missing.txt) · [03-ambiguous](../code/part-1/day-07-llm-extraction/samples/emails/03-ambiguous.txt) · [07-date-format](../code/part-1/day-07-llm-extraction/samples/emails/07-date-format.txt) · [results](../code/part-1/day-07-llm-extraction/README.md#results) |
| Measures the effect of a prompt change | | [v1 against v2](../code/part-1/day-07-llm-extraction/README.md#v1-against-v2) · [NOTES.md](../code/part-1/day-07-llm-extraction/NOTES.md) |

## Key learnings

_To write: calling an LLM API (system prompt, temperature, token limits, cost) · what makes a prompt reliable · structured outputs · sending a PDF and its limits · why LLM output can be confidently wrong and how to reduce it._

## Exercises

### Exercise 1: Extract named fields from an email into a validated schema

Spec: [SPEC.md](../code/part-1/day-07-llm-extraction/SPEC.md) · Code and decisions: [README](../code/part-1/day-07-llm-extraction/README.md) · Notes: [NOTES.md](../code/part-1/day-07-llm-extraction/NOTES.md)

_To write: summary of what you built._

### Exercise 2: Five emails, one with missing information

Ten made-up emails (the first five, three harder ones and two unseen ones), with expected values written before each run. Missing and ambiguous cases are `02-missing`, `03-ambiguous` and `07-date-format`. See the [results](../code/part-1/day-07-llm-extraction/README.md#results).

### Exercise 3: One PDF invoice checked against the document

Two invoices (simple and hard), each field checked against the PDF. See the [invoice results](../code/part-1/day-07-llm-extraction/README.md#invoice-results).

### Exercise 4: Change the prompt and measure

Prompt v1 (bare) against v2 (one complete prompt) on the same emails. See [v1 against v2](../code/part-1/day-07-llm-extraction/README.md#v1-against-v2).

_To write: what the change did and did not fix._

## Reflection

_To write (yours): what makes a prompt reliable rather than lucky?_

## AI use

_To write (yours)._

## Open questions

-
