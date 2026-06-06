from __future__ import annotations

import pandas as pd

from app.data_model import Scenario


ACTIONS = [
    "Shift flexible residential loads to off-peak windows",
    "Stagger commercial cooling and lighting loads",
    "Schedule pump/borewell loads away from evening peak",
    "Adaptive streetlight dimming after low-footfall hours",
    "Transformer monitoring/maintenance priority",
    "Rooftop solar or battery buffering recommendation",
    "No aggressive intervention required",
]


def _objective_weights(objective: str) -> dict[str, float]:
    if objective == "Maximise peak reduction":
        return {"peak": 1.45, "cost": 0.9, "relief": 1.2, "carbon": 0.8}
    if objective == "Minimise comfort disruption":
        return {"peak": 0.8, "cost": 0.7, "relief": 0.9, "carbon": 0.7}
    if objective == "Prioritise infrastructure relief":
        return {"peak": 1.0, "cost": 0.8, "relief": 1.55, "carbon": 0.8}
    return {"peak": 1.0, "cost": 1.2, "relief": 1.0, "carbon": 1.2}


def utility_formula_text(objective: str) -> str:
    weights = _objective_weights(objective)
    return (
        "Utility = "
        f"{weights['peak']:.2f}*peak reduction + "
        f"{weights['cost']:.2f}*cost saving + "
        f"{weights['relief']:.2f}*infrastructure relief + "
        f"{weights['carbon']:.2f}*carbon proxy reduction - comfort penalty - safety penalty"
    )


def rank_actions(scenario: Scenario, peak_risk: float, stress: float) -> pd.DataFrame:
    weights = _objective_weights(scenario.objective)
    evening = 18 <= scenario.hour <= 22
    late_night = scenario.hour >= 23 or scenario.hour <= 5
    high_critical = scenario.critical_load_pct >= 45

    base = {
        ACTIONS[0]: (24, 18, 15, 12, 16, 4),
        ACTIONS[1]: (28 if scenario.zone_type in {"Commercial", "Mixed", "Market", "Public-Commercial"} else 10, 20, 18, 14, 12, 5),
        ACTIONS[2]: (22 if evening else 12, 14, 16, 10, 10, 4),
        ACTIONS[3]: (20 if scenario.zone_type == "Street Lighting" or late_night else 8, 12, 10, 18, 8, 2),
        ACTIONS[4]: (12, 6, 30 if scenario.transformer_load_ratio > 0.8 else 16, 8, 5, 3),
        ACTIONS[5]: (18, 22, 18, 26, 4, 2),
        ACTIONS[6]: (4, 2, 3, 2, 0, 0),
    }

    rows = []
    for action, (peak, cost, relief, carbon, comfort_penalty, safety_penalty) in base.items():
        rule_fit = 45
        if evening and action in {ACTIONS[0], ACTIONS[1], ACTIONS[2]}:
            peak += 10
            relief += 6
            rule_fit += 18
        if high_critical and action != ACTIONS[4]:
            safety_penalty += 8
            comfort_penalty += 7
            rule_fit -= 10
        if peak_risk < 45 and action == ACTIONS[6]:
            peak += 18
            cost += 10
            comfort_penalty = 0
            rule_fit += 25
        if stress > 75 and action == ACTIONS[4]:
            relief += 14
            rule_fit += 24
        if scenario.zone_type == "Street Lighting" and action == ACTIONS[3]:
            peak += 8
            carbon += 10
            rule_fit += 24
        if scenario.zone_type == "Residential" and action == ACTIONS[0]:
            peak += 8
            cost += 6
            rule_fit += 18

        utility = (
            peak * weights["peak"]
            + cost * weights["cost"]
            + relief * weights["relief"]
            + carbon * weights["carbon"]
            - comfort_penalty
            - safety_penalty
        )
        rows.append(
            {
                "Action": action,
                "Peak reduction": peak,
                "Cost saving": cost,
                "Infrastructure relief": relief,
                "Carbon proxy reduction": carbon,
                "Comfort penalty": comfort_penalty,
                "Safety penalty": safety_penalty,
                "Rule fit": max(0, min(100, rule_fit)),
                "Utility score": round(max(0, utility), 1),
            }
        )

    ranked = pd.DataFrame(rows).sort_values("Utility score", ascending=False).reset_index(drop=True)
    return ranked
