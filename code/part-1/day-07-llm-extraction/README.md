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
| **Total** | | | | | | | **28/30** |
