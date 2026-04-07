"""Grading logic for the Incident Response Environment (0.0–1.0 scale)."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .scenarios import Scenario


@dataclass
class EpisodeHistory:
    """Tracks agent actions throughout an episode."""

    root_cause_declared: Optional[str] = None
    root_cause_correct: bool = False
    root_cause_partial: bool = False

    remedies_attempted: List[Dict[str, str]] = field(default_factory=list)
    remedy_correct: bool = False

    services_queried_logs: Set[str] = field(default_factory=set)
    services_queried_metrics: Set[str] = field(default_factory=set)
    services_queried_runbook: Set[str] = field(default_factory=set)
    relevant_clues_found: int = 0

    steps_used: int = 0
    noop_count: int = 0

    wrong_remedies: int = 0
    destructive_actions: int = 0
    unnecessary_escalations: int = 0
    invalid_actions: int = 0


def check_root_cause(declared: str, scenario: Scenario) -> tuple[bool, bool]:
    """Returns (exact_match, partial_match) based on keyword overlap."""
    if not declared:
        return False, False

    declared_lower = declared.lower()
    matched = sum(1 for kw in scenario.root_cause_keywords if kw.lower() in declared_lower)

    if matched >= 3:
        return True, True
    elif matched >= 1:
        return False, True
    return False, False


def check_remedy(attempted: List[Dict[str, str]], scenario: Scenario) -> bool:
    """Check if any attempted remedy matches a valid remedy."""
    for attempt in attempted:
        a_service = attempt.get("service", "").lower().strip()
        a_remedy = attempt.get("remedy", "").lower().strip()

        for valid in scenario.valid_remedies:
            v_service = valid["service"].lower().strip()
            v_remedy = valid["remedy"].lower().strip()

            if a_service == v_service and (v_remedy in a_remedy or a_remedy in v_remedy):
                return True
    return False


def grade_episode(scenario: Scenario, history: EpisodeHistory) -> float:
    """Grade episode: root_cause(0.30) + remedy(0.35) + efficiency(0.15) + clues(0.20) - penalties."""
    score = 0.0

    if history.root_cause_correct:
        score += 0.30
    elif history.root_cause_partial:
        score += 0.10

    if history.remedy_correct:
        score += 0.35

    if scenario.max_steps > 0 and history.steps_used > 0:
        ratio = history.steps_used / scenario.max_steps
        if ratio <= 0.4:
            score += 0.15
        elif ratio <= 0.6:
            score += 0.12
        elif ratio <= 0.8:
            score += 0.08
        else:
            score += 0.04

    if scenario.total_clues > 0:
        score += 0.20 * min(1.0, history.relevant_clues_found / scenario.total_clues)

    score -= 0.15 * history.wrong_remedies
    score -= 0.30 * history.destructive_actions
    score -= 0.10 * history.unnecessary_escalations

    return round(max(0.01, min(0.99, score)), 4)


def get_grade_breakdown(scenario: Scenario, history: EpisodeHistory) -> Dict[str, float]:
    """Detailed score breakdown for debugging."""
    b = {}

    b["root_cause"] = 0.30 if history.root_cause_correct else (0.10 if history.root_cause_partial else 0.0)
    b["remedy"] = 0.35 if history.remedy_correct else 0.0

    if scenario.max_steps > 0 and history.steps_used > 0:
        ratio = history.steps_used / scenario.max_steps
        b["efficiency"] = 0.15 if ratio <= 0.4 else (0.12 if ratio <= 0.6 else (0.08 if ratio <= 0.8 else 0.04))
    else:
        b["efficiency"] = 0.0

    if scenario.total_clues > 0:
        b["clue_discovery"] = round(0.20 * min(1.0, history.relevant_clues_found / scenario.total_clues), 4)
    else:
        b["clue_discovery"] = 0.0

    b["penalty_wrong_remedy"] = -0.15 * history.wrong_remedies
    b["penalty_destructive"] = -0.30 * history.destructive_actions
    b["penalty_escalation"] = -0.10 * history.unnecessary_escalations
    b["total"] = grade_episode(scenario, history)

    return b
