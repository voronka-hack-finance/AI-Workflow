"""Normalization warning collector."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NormalizationWarnings:
    warnings: list[str] = field(default_factory=list)
    unmapped_categories: list[str] = field(default_factory=list)
    ambiguous_transactions: list[str] = field(default_factory=list)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_unmapped_category(self, category: str) -> None:
        if category not in self.unmapped_categories:
            self.unmapped_categories.append(category)

    def add_ambiguous_transaction(self, transaction_id: str) -> None:
        if transaction_id not in self.ambiguous_transactions:
            self.ambiguous_transactions.append(transaction_id)
