# LLM extraction from email and PDF

Spec: [SPEC.md](SPEC.md) · Notes: [NOTES.md](NOTES.md)

## Samples and expected values

Five made-up emails in [samples/emails/](samples/emails/) and one made-up invoice in [samples/invoice.pdf](samples/invoice.pdf). The expected values below were written from the sample texts before the emails were run (the invoice was tried once with prompt v1 before this table was written, so its values come from the PDF itself).

### How a field is marked correct

| Field | Correct when |
| --- | --- |
| `sender` | It names the right person or company. An added email address is accepted. |
| `date` | It names the right calendar day, in any format. A relative date such as "next Friday" is not a calendar day, so the expected value is `None`. |
| `amount` | The number is exactly right. An approximate amount ("about 500") is not a figure, so the expected value is `None`. |
| `currency` | The right ISO code, or `None` when no currency is stated. |
| `reference` | Exactly right, or `None` when there is no reference. |
| `purpose` | Same meaning, judged by eye. |

### Emails

| File | sender | date | amount | currency | reference | purpose |
| --- | --- | --- | --- | --- | --- | --- |
| `01-clean` | Priya Nair | 2026-03-14 | 1250.00 | USD | BL-4821 | payment received for an annual software licence renewal |
| `02-missing` | Marcus Webb | `None` | `None` | `None` | TKT-7730 | asking for the status of a delayed parcel |
| `03-ambiguous` | Lena Fischer | `None` | `None` | EUR | `None` | paying a venue deposit |
| `04-meeting` | Tom Alvarez | 2026-04-22 | `None` | `None` | `None` | scheduling the project kickoff meeting |
| `05-two-amounts` | Sofia Rossi | 2026-06-30 | 200.00 | GBP | INV-884 | asking for payment of the remaining balance |

What each one tests: `02` has no date or amount (must be `None`, not invented). `03` has a vague date and amount. `05` has several amounts and dates, and the right ones are the remaining balance and its deadline.

### Invoice

| Field | Expected (from the PDF) |
| --- | --- |
| `sender` | Northwind Stationery Ltd |
| `date` | 2026-02-03 (the invoice date, not the 5 March due date) |
| `amount` | 266.40 (total due, not the 222.00 subtotal) |
| `currency` | GBP |
| `reference` | INV-20431 |
| `purpose` | supply of stationery (A4 paper and pens) |

## Harder samples

Added after the v1 baseline scored 28/30 on the first five emails, because that left little room to show improvement. The expected values below were written before these were run. The matching rules above apply.

### Emails

| File | sender | date | amount | currency | reference | purpose |
| --- | --- | --- | --- | --- | --- | --- |
| `06-correction` | Daniel Okafor | 2026-07-20 | 1020.00 | USD | QT-3382 | paying the conference booth fee |
| `07-date-format` | Hannah Boyd | `None` | `None` | `None` | `None` | announcing a training session |
| `08-european-format` | Klaus Weber | 2026-09-30 | 1234.50 | EUR | RE-20871 | paying an invoice |

What each one tests: `06` has a corrected amount, so the old figure 1,200 and the old date in the quoted text are distractors. `07` has the date `03/04/2026`, which is 3 April or 4 March, so it must be `None`. `08` has the amount `1.234,50 €` (European format), and the reference is the invoice number, not the purchase order `PO-4412`.

### Invoice (hard): [samples/invoice-hard.pdf](samples/invoice-hard.pdf)

One page with a discount, shipping, VAT, a balance brought forward, and an invoice total that differs from the amount due.

| Field | Expected (from the PDF) |
| --- | --- |
| `sender` | Lakeshore Print & Pack Ltd |
| `date` | 2026-05-12 (the invoice date, not the 11 June due date) |
| `amount` | 1380.00 (the "Amount due", which includes the 150.00 brought forward, not the 1,230.00 invoice total) |
| `currency` | USD |
| `reference` | LP-77231 (the invoice number, not `PO-5590` or the old `LP-76902`) |
| `purpose` | supply of custom boxes and printed labels |

## Unseen emails

Two more emails, added to check that the improved prompt (v2) works beyond the cases it was written for. v2 was drafted knowing the misses on emails 01 to 08, so scores on those are weaker evidence. These two use situations v2 does not mention. The matching rules above apply.

| File | sender | date | amount | currency | reference | purpose |
| --- | --- | --- | --- | --- | --- | --- |
| `09-card-charge` | Maya Chen | 2026-08-09 | 85.00 | USD | OR-5521 | a card charge for an order of one wireless mouse |
| `10-quote` | Arjun Mehta | `None` | 4800.00 | INR | Q-3307 | quotation for 12 office chairs |

What each one tests: `09` has a `$` sign and a US-style date ("Aug 9, 2026"). `10` has a total and a GST amount (the total is the figure), and "valid for 30 days", which is a period and not a date, so `date` must be `None`.

## Invoice results

The same extraction on a PDF: `extract("samples/invoice.pdf")` sends the file itself to the model, with no text extraction first. Saved outputs: [v1](samples/outputs/invoice-v1.json), [v2](samples/outputs/v2/invoice.json).

### Simple invoice: [samples/invoice.pdf](samples/invoice.pdf)

| Field | Expected (from the PDF) | v1 | v2 |
| --- | --- | --- | --- |
| `sender` | Northwind Stationery Ltd | ✓ Northwind Stationery Ltd | ✓ Northwind Stationery Ltd |
| `date` | 2026-02-03 (invoice date) | ✓ 3 February 2026 | ✗ 2026-03-05 (the due date) |
| `amount` | 266.40 (total due) | ✓ 266.4 | ✓ 266.4 |
| `currency` | GBP | ✓ GBP | ✓ GBP |
| `reference` | INV-20431 | ✓ INV-20431 | ✓ INV-20431 |
| `purpose` | supply of stationery (A4 paper and pens) | ✓ A4 paper and pens (the line items) | ✓ payment for stationery supplies |
| **Score** | | **6/6** | **5/6** |

Both invoices lost the same point with v2: it picks the due date, not the invoice date. So the date rule in v2 ("for a payment request use the payment deadline") is the likely cause, since an invoice is also a payment request. The hard invoice is in the harder samples section above.

### PDF limits

From the Gemini documentation (document understanding): a PDF can be up to 50 MB or 1,000 pages, and each page costs about 258 tokens. This applies to inline data, which is how `extract()` sends the file, and to the Files API. Larger documents that are reused across several requests are better sent through the Files API. Each sample invoice here is one page and under 50 KB. Scanned and multi-page PDFs were not tried.

Source: [Document understanding | Gemini API](https://ai.google.dev/gemini-api/docs/document-processing)

## Results

Outputs are saved in [samples/outputs/](samples/outputs/). Each cell is what the model returned, marked ✓ or ✗ against the expected value above.

### Prompt v1 (baseline): `Extract the information from this document.`

| File | sender | date | amount | currency | reference | purpose | Score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `01-clean` | ✓ Priya Nair (with address) | ✓ 14 March 2026 | ✓ 1250.0 | ✓ USD | ✓ BL-4821 | ✓ annual software licence renewal | 6/6 |
| `02-missing` | ✓ Marcus Webb | ✓ `None` | ✓ `None` | ✓ `None` | ✓ TKT-7730 | ✓ inquiry about parcel delivery status | 6/6 |
| `03-ambiguous` | ✓ Lena Fischer | ✓ `None` | ✗ 500.0 (expected `None`) | ✓ EUR | ✓ `None` | ✓ deposit for the venue | 5/6 |
| `04-meeting` | ✓ Tom Alvarez (with address) | ✓ 22 April 2026 | ✓ `None` | ✓ `None` | ✓ `None` | ✓ project kickoff meeting | 6/6 |
| `05-two-amounts` | ✓ Sofia Rossi (with address) | ✗ 15 June 2026 (expected 30 June, the deadline) | ✓ 200.0 | ✓ GBP | ✓ INV-884 | ✓ outstanding balance payment | 5/6 |
| `06-correction` | ✓ Daniel Okafor | ✓ 20 July 2026 | ✓ 1020.0 | ✓ USD | ✓ QT-3382 | ✓ conference booth fee | 6/6 |
| `07-date-format` | ✓ Hannah Boyd (with address) | ✗ `03/04/2026` (expected `None`; it kept the raw text and did not pick a reading) | ✓ `None` | ✓ `None` | ✓ `None` | ✓ training session | 5/6 |
| `08-european-format` | ✓ Klaus Weber (with address) | ✓ 30 September 2026 | ✓ 1234.5 | ✓ EUR | ✓ RE-20871 | ✗ `PO-4412` (that is a reference, not a purpose) | 5/6 |
| `09-card-charge` | ✓ Maya Chen (with address) | ✓ Aug 9, 2026 | ✓ 85.0 | ✓ USD | ✓ OR-5521 | ✓ one wireless mouse | 6/6 |
| `10-quote` | ✓ Arjun Mehta | ✓ `None` | ✓ 4800.0 | ✓ INR | ✓ Q-3307 | ✓ office chairs | 6/6 |
| **Total (10 emails)** | | | | | | | **56/60** |

The first five emails scored 28/30, the three harder ones 16/18, and the two unseen ones 12/12.

### Prompt v2 (one complete prompt)

The full text is in [prompts.py](prompts.py): field definitions, "null when not stated, never guess", rules for relative, ambiguous and approximate values, and tie-breaking for corrected figures and amounts due.

| File | sender | date | amount | currency | reference | purpose | Score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `01-clean` | ✓ Priya Nair | ✓ 2026-03-14 | ✓ 1250.0 | ✓ USD | ✓ BL-4821 | ✓ annual software licence renewal | 6/6 |
| `02-missing` | ✓ Marcus Webb | ✓ `None` | ✓ `None` | ✓ `None` | ✓ TKT-7730 | ✓ delivery status inquiry | 6/6 |
| `03-ambiguous` | ✓ Lena Fischer | ✓ `None` | ✓ `None` (was 500.0) | ✓ EUR | ✓ `None` | ✓ venue deposit | 6/6 |
| `04-meeting` | ✓ Tom Alvarez | ✓ 2026-04-22 | ✓ `None` | ✓ `None` | ✓ `None` | ✓ project kickoff meeting | 6/6 |
| `05-two-amounts` | ✓ Sofia Rossi | ✓ 2026-06-30 (was 15 June) | ✓ 200.0 | ✓ GBP | ✓ INV-884 | ✓ outstanding balance payment | 6/6 |
| `06-correction` | ✓ Daniel Okafor | ✓ 2026-07-20 | ✓ 1020.0 | ✓ USD | ✓ QT-3382 | ✓ conference booth fee | 6/6 |
| `07-date-format` | ✓ Hannah Boyd | ✓ `None` (was `03/04/2026`) | ✓ `None` | ✓ `None` | ✓ `None` | ✓ training session | 6/6 |
| `08-european-format` | ✗ Alpenwerk (expected Klaus Weber; the company name comes only from the email domain) | ✓ 2026-09-30 | ✓ 1234.5 | ✓ EUR | ✓ RE-20871 | ✓ invoice payment (was `PO-4412`) | 5/6 |
| `09-card-charge` | ✓ Maya Chen | ✓ 2026-08-09 | ✓ 85.0 | ✓ USD | ✓ OR-5521 | ✓ order confirmation | 6/6 |
| `10-quote` | ✓ Arjun Mehta | ✓ `None` | ✓ 4800.0 | ✓ INR | ✓ Q-3307 | ✓ quotation for office chairs | 6/6 |
| **Total (10 emails)** | | | | | | | **59/60** |

### Hard invoice, prompt v2

| Field | Expected | Got | Correct? |
| --- | --- | --- | --- |
| `sender` | Lakeshore Print & Pack Ltd | Lakeshore Print & Pack Ltd | ✓ |
| `date` | 2026-05-12 | 2026-06-11 | ✗ (the due date; v1 had the invoice date right) |
| `amount` | 1380.00 | 1380.0 | ✓ |
| `currency` | USD | USD | ✓ |
| `reference` | LP-77231 | LP-77231 | ✓ |
| `purpose` | custom boxes and printed labels | payment for custom boxes and printed labels | ✓ |

Score 5/6.

### v1 against v2

| Set | v1 | v2 |
| --- | --- | --- |
| Emails 01 to 08 (v2 was written knowing their misses) | 44/48 | 47/48 |
| Unseen emails 09 and 10 | 12/12 | 12/12 |
| All 10 emails | 56/60 | 59/60 |
| Simple invoice | 6/6 | 5/6 |
| Hard invoice | 6/6 | 5/6 |

v2 fixed four misses (the approximate amount in `03`, the wrong deadline in `05`, the raw date in `07`, the PO number in `purpose` for `08`). It added two kinds of miss: `sender` in `08` (it guessed a company from the email domain) and `date` on both invoices (it took the due date). The unseen emails show no difference, because v1 already got them all right, so they cannot show whether v2 generalizes.

### Hard invoice, prompt v1

| Field | Expected | Got | Correct? |
| --- | --- | --- | --- |
| `sender` | Lakeshore Print & Pack Ltd | Lakeshore Print & Pack Ltd | ✓ |
| `date` | 2026-05-12 | 12 May 2026 | ✓ |
| `amount` | 1380.00 | 1380.0 | ✓ (it chose "Amount due", not the invoice total) |
| `currency` | USD | USD | ✓ |
| `reference` | LP-77231 | LP-77231 | ✓ |
| `purpose` | custom boxes and printed labels | Custom boxes and Printed labels | ✓ |

Score 6/6.
