from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from finance_close_control_tower.validations import SEVERITY_RANK, ValidationResult


@dataclass(frozen=True)
class CloseReadinessScore:
    entity: str
    period: str
    process_area: str
    score: float
    status: str
    top_drivers: tuple[str, ...]
    exception_count: int


PROCESS_WEIGHTS = {
    "trial_balance": 20,
    "reconciliations": 20,
    "suspense": 15,
    "bank_rec": 15,
    "vat": 15,
    "intercompany": 15,
}

SEVERITY_PENALTIES = {
    "critical": 100,
    "high": 45,
    "warning": 20,
    "info": 0,
}


def _status_from_score(score: float, has_critical: bool = False) -> str:
    if has_critical or score < 70:
        return "red"
    if score < 90:
        return "amber"
    return "green"


def _all_entity_periods(datasets: dict[str, pd.DataFrame]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for frame in datasets.values():
        if "entity" in frame.columns and "period" in frame.columns:
            for _, row in frame[["entity", "period"]].drop_duplicates().iterrows():
                pairs.add((str(row["entity"]), str(row["period"])))
    return pairs


def calculate_process_scores(
    datasets: dict[str, pd.DataFrame],
    validation_results: list[ValidationResult],
) -> list[CloseReadinessScore]:
    scores: list[CloseReadinessScore] = []
    entity_periods = sorted(_all_entity_periods(datasets))

    for entity, period in entity_periods:
        for process_area in PROCESS_WEIGHTS:
            relevant = [
                result
                for result in validation_results
                if result.process_area == process_area
                and result.period == period
                and (result.entity == entity or (result.entity and entity in result.entity))
            ]
            penalty = min(sum(SEVERITY_PENALTIES[result.severity] for result in relevant), 100)
            score = max(100.0 - penalty, 0.0)
            has_critical = any(result.severity == "critical" for result in relevant)
            drivers = tuple(
                result.message
                for result in sorted(
                    relevant,
                    key=lambda item: SEVERITY_RANK[item.severity],
                    reverse=True,
                )[:5]
            )
            scores.append(
                CloseReadinessScore(
                    entity=entity,
                    period=period,
                    process_area=process_area,
                    score=score,
                    status=_status_from_score(score, has_critical),
                    top_drivers=drivers or ("No exceptions detected.",),
                    exception_count=len(relevant),
                )
            )

    return scores


def calculate_overall_scores(process_scores: list[CloseReadinessScore]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    grouped: dict[tuple[str, str], list[CloseReadinessScore]] = {}
    for score in process_scores:
        grouped.setdefault((score.entity, score.period), []).append(score)

    for (entity, period), scores in sorted(grouped.items()):
        weighted_total = sum(
            score.score * PROCESS_WEIGHTS[score.process_area] for score in scores
        ) / sum(PROCESS_WEIGHTS.values())
        has_critical = any(score.status == "red" and score.score == 0 for score in scores)
        top_drivers = [
            driver
            for score in sorted(scores, key=lambda item: item.score)
            for driver in score.top_drivers
            if driver != "No exceptions detected."
        ][:5]
        rows.append(
            {
                "entity": entity,
                "period": period,
                "score": round(weighted_total, 1),
                "status": _status_from_score(weighted_total, has_critical),
                "exception_count": sum(score.exception_count for score in scores),
                "top_drivers": top_drivers or ["No exceptions detected."],
            }
        )

    return pd.DataFrame(rows)


def process_scores_to_frame(process_scores: list[CloseReadinessScore]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "entity": score.entity,
                "period": score.period,
                "process_area": score.process_area,
                "score": score.score,
                "status": score.status,
                "exception_count": score.exception_count,
                "top_drivers": "; ".join(score.top_drivers),
            }
            for score in process_scores
        ]
    )
