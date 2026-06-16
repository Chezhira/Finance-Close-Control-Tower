from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CloseControlConfig:
    tb_tolerance: float = 0.01
    vat_tolerance: float = 0.01
    suspense_materiality: float = 5_000.0
    suspense_ageing_days: int = 30
    bank_exception_ageing_days: int = 14
    max_upload_mb: int = 10
    max_rows_per_file: int = 50_000
    pii_scan_enabled: bool = True
    strict_synthetic_mode: bool = True
    rule_version: str = "mvp-0.1.0"


DEFAULT_CONFIG = CloseControlConfig()
