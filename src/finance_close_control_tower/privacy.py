from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
DEFAULT_BANNED_TERMS = (
    "confidential",
    "private bank",
    "payroll",
    "real employer",
    "client secret",
)
PHONE_EXEMPT_COLUMN_TOKENS = ("account", "code", "date", "id", "no", "period", "ref")


@dataclass(frozen=True)
class PrivacyFinding:
    source: str
    column: str
    finding_type: str
    row_count: int


class PrivacyViolation(ValueError):
    """Raised when public-demo guardrails detect private or personal data."""


def scan_dataframe(
    frame: pd.DataFrame,
    *,
    source: str,
    banned_terms: tuple[str, ...] = DEFAULT_BANNED_TERMS,
) -> list[PrivacyFinding]:
    findings: list[PrivacyFinding] = []
    string_columns = frame.select_dtypes(include=["object", "string"]).columns

    for column in string_columns:
        series = frame[column].dropna().astype(str)
        if series.empty:
            continue

        email_hits = series.str.contains(EMAIL_PATTERN, regex=True).sum()
        if email_hits:
            findings.append(PrivacyFinding(source, column, "email", int(email_hits)))

        if not any(token in column.lower() for token in PHONE_EXEMPT_COLUMN_TOKENS):
            phone_hits = series.str.contains(PHONE_PATTERN, regex=True).sum()
            if phone_hits:
                findings.append(PrivacyFinding(source, column, "phone_like", int(phone_hits)))

        lowered = series.str.lower()
        for term in banned_terms:
            term_hits = lowered.str.contains(re.escape(term.lower()), regex=True).sum()
            if term_hits:
                findings.append(
                    PrivacyFinding(source, column, f"banned_term:{term}", int(term_hits))
                )

    return findings


def scan_file(frame: pd.DataFrame, path: Path) -> None:
    findings = scan_dataframe(frame, source=path.name)
    if findings:
        summary = ", ".join(
            f"{finding.source}:{finding.column}:{finding.finding_type}" for finding in findings
        )
        raise PrivacyViolation(f"Privacy scan failed for {path.name}: {summary}")
