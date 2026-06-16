from __future__ import annotations

import pandas as pd
import pytest

from finance_close_control_tower.privacy import PrivacyViolation, scan_dataframe, scan_file


def test_privacy_scan_flags_email() -> None:
    frame = pd.DataFrame({"owner": ["person@example.com"]})
    findings = scan_dataframe(frame, source="unit-test.csv")
    assert findings
    assert findings[0].finding_type == "email"


def test_privacy_scan_flags_banned_terms() -> None:
    frame = pd.DataFrame({"description": ["confidential payroll extract"]})
    findings = scan_dataframe(frame, source="unit-test.csv")
    finding_types = {finding.finding_type for finding in findings}
    assert "banned_term:confidential" in finding_types
    assert "banned_term:payroll" in finding_types


def test_scan_file_raises_for_private_data() -> None:
    frame = pd.DataFrame({"owner": ["person@example.com"]})
    with pytest.raises(PrivacyViolation):
        scan_file(frame, path=type("PathLike", (), {"name": "unsafe.csv"})())
