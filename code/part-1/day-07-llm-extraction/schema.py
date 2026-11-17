from pydantic import BaseModel


class Extraction(BaseModel):
    """Fields pulled from an email or an invoice. Every field is optional:
    if the input does not contain a value, None is the correct answer."""

    sender: str | None = None
    date: str | None = None
    amount: float | None = None
    currency: str | None = None
    reference: str | None = None
    purpose: str | None = None
