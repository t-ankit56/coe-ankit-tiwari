# Success criteria

What "correct" means for `extract()`, written before any eval run. The test set is in [cases.json](cases.json). The expected values come from the Day 7 README tables, which were written before the Day 7 runs.

## Field rules

The rules are the Day 7 rules, so the results are comparable with Day 7.

| Field | Correct when |
| --- | --- |
| `sender` | The expected name appears in the answer, ignoring case. An added address or email is fine. |
| `date` | It is the same calendar day as expected, in any common format (`2026-03-14`, `14 March 2026`, `Aug 9, 2026`). When `None` is expected, the answer must be `None`: a relative date, an ambiguous one (`03/04/2026`) or a period ("valid for 30 days") filled in as a date is a failure. |
| `amount` | The number is exactly right. When `None` is expected, the answer must be `None`: an approximate figure ("about 500") is a failure. |
| `currency` | The exact ISO code, or `None` when the input states none. |
| `reference` | Exactly right, or `None` when the input has none. |
| `purpose` | Not matched exactly. DeepEval `GEval` scores whether it has the same meaning as the expected purpose and contains no identifier (Step 3). |

A value filled in where `None` is expected is always a failure: inventing a value is the mistake the eval most needs to catch.

## Pass rules

- A **case** passes when all five exact fields (`sender`, `date`, `amount`, `currency`, `reference`) are correct.
- The **run** passes when the share of passing cases is at or above `PASS_RATE`.
- The `purpose` score has its own threshold and is reported next to the pass rate.

`PASS_RATE` and the `purpose` threshold are not set yet. They are set from the first real run of prompt v2 and recorded in [NOTES.md](NOTES.md) with the reason, so they are not guessed here.

## What the test set covers

12 cases: 10 emails and 2 PDF invoices.

| Case | What it tests |
| --- | --- |
| `01-clean` | A plain email where every field is stated. |
| `02-missing` | No date or amount: the answer must be `None`, not invented. |
| `03-ambiguous` | A vague date and an approximate amount. |
| `04-meeting` | A meeting date and no amount. |
| `05-two-amounts` | Several amounts and dates: the remaining balance and its deadline are right. |
| `06-correction` | A corrected amount: the old figure and the old date in quoted text are distractors. |
| `07-date-format` | `03/04/2026` can be read two ways, so `date` must be `None`. |
| `08-european-format` | `1.234,50 €`, and the invoice number is the reference, not the purchase order. |
| `09-card-charge` | A `$` sign and a US-style date. |
| `10-quote` | A total and a tax amount (the total is the figure), and "valid for 30 days", which is not a date. |
| `invoice` | A PDF where the invoice date and the total due are the right ones, not the due date or the subtotal. |
| `invoice-hard` | A PDF with discount, shipping, VAT and a balance brought forward: "Amount due" is the figure. |

12 cases is a small sample. One case is about 8 points of pass rate, so a small change in the pass rate is within noise. The model's output is also probabilistic, so the same case can pass in one run and fail in the next.
