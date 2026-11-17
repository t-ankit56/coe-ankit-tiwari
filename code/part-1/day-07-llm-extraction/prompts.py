PROMPTS = {
    # Deliberately bare: the baseline that v2 is measured against.
    "v1": "Extract the information from this document.",
    # One complete prompt: field definitions, null rules and tie-breaking.
    "v2": """You extract structured data from an email or a document such as an invoice.
Fill only the fields in the schema.

Fields:
- sender: the person or company that sent the email or issued the document.
  Name only, without an email address.
- date: the one date the message is about, as YYYY-MM-DD. For a payment
  request use the payment deadline. For an invoice use the invoice date.
  For a meeting or event use the date of the event.
- amount: the one amount that is owed or being confirmed, as a plain number
  with no currency symbol or thousands separator. If a figure was corrected,
  use the corrected one. If there is an "amount due" or a remaining balance,
  use that rather than the original total.
- currency: the ISO 4217 code, such as USD, EUR or GBP.
- reference: the identifier of the invoice, ticket, order or quote the
  message is about. Prefer the sender's own invoice number over a purchase
  order number.
- purpose: a short phrase (under 10 words) for what the message is about.
  Never put an identifier in it.

Rules:
- Use null for any field that is not stated. Never guess or infer a value.
- Use null for the date if it is relative ("next Friday") or can be read
  two ways (such as 03/04/2026).
- Use null for the amount if it is only approximate ("about 500").
- Text quoted from earlier messages is background. Use the newest message.
""",
}
