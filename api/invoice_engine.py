"""Wave 135 — Invoice Engine.

Generates, tracks, and settles invoices for delivered work. Invoices
carry line items from contracts and commissions; the engine records
payment status and escalates overdue accounts to the civilization's
collections process.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

STATUSES = ["draft", "issued", "paid", "overdue"]


class Invoice:
    """A billing statement for delivered work."""

    def __init__(self, client: str, line_items: Dict[str, float]):
        self.client = client
        self.line_items = dict(line_items)
        self.total = round(sum(line_items.values()), 4)
        self.status = "draft"
        self.paid_amount = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"invoice:{client}".encode()).hexdigest()[:10]

    def issue(self) -> bool:
        if self.status != "draft":
            return False
        self.status = "issued"
        return True

    def pay(self, amount: float) -> bool:
        if self.status not in ("issued", "overdue"):
            return False
        self.paid_amount += amount
        if self.paid_amount >= self.total - 0.001:
            self.status = "paid"
        return True

    def mark_overdue(self) -> bool:
        if self.status != "issued":
            return False
        self.status = "overdue"
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "client": self.client, "total": self.total,
                "paid": round(self.paid_amount, 4), "status": self.status}


class InvoiceEngine:
    """Generates and settles the civilization's invoices."""

    def __init__(self):
        self._invoices: Dict[str, Invoice] = {}
        self._collected = 0.0
        self._overdue_count = 0

    def create(self, client: str, line_items: Dict[str, float], issue: bool = True) -> Invoice:
        invoice = Invoice(client, line_items)
        self._invoices[invoice.id] = invoice
        if issue:
            invoice.issue()
        return invoice

    def pay(self, invoice_id: str, amount: float) -> bool:
        invoice = self._invoices.get(invoice_id)
        if invoice is None:
            return False
        ok = invoice.pay(amount)
        if ok and invoice.status == "paid":
            self._collected += invoice.total
        return ok

    def escalate(self, invoice_id: str) -> bool:
        invoice = self._invoices.get(invoice_id)
        if invoice is None:
            return False
        ok = invoice.mark_overdue()
        if ok:
            self._overdue_count += 1
        return ok

    def status(self) -> Dict[str, Any]:
        return {"invoices": len(self._invoices),
                "collected": round(self._collected, 4),
                "overdue": self._overdue_count,
                "outstanding": round(
                    sum(i.total - i.paid_amount for i in self._invoices.values()
                        if i.status != "paid"), 4)}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    engine = InvoiceEngine()
    return {"status": "active", "module": "invoice_engine",
            **engine.status()}
