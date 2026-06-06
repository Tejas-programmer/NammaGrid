from __future__ import annotations

from app.data_model import Scenario
from app.optimizer import ACTIONS


def fired_rules(scenario: Scenario, peak_risk: float, stress: float) -> list[str]:
    rules: list[str] = []
    evening = 18 <= scenario.hour <= 22
    late_night = scenario.hour >= 23 or scenario.hour <= 5

    if evening:
        rules.append("R1: Evening 18-22 peak window is active.")
    if scenario.zone_type in {"Commercial", "Mixed", "Market", "Public-Commercial"} and evening:
        rules.append("R2: Commercial or mixed evening load needs staggered cooling and lighting.")
    if scenario.zone_type == "Residential" and evening and scenario.flexible_load_pct >= 20:
        rules.append("R3: Residential flexible load can be shifted away from the peak.")
    if scenario.zone_type == "Street Lighting" and late_night:
        rules.append("R4: Streetlight load is night-heavy, so adaptive dimming is allowed after low-footfall hours.")
    if scenario.transformer_load_ratio > 0.8 or stress >= 70:
        rules.append("R5: Transformer stress is high enough to prioritise monitoring or maintenance.")
    if scenario.critical_load_pct >= 45:
        rules.append("R6: Critical load is high, so aggressive interventions are penalised.")
    if peak_risk < 45:
        rules.append("R7: Peak risk is low, so no aggressive intervention is preferred.")
    return rules


def expert_recommendations(scenario: Scenario, peak_risk: float, stress: float) -> list[str]:
    recommendations: list[str] = []
    evening = 18 <= scenario.hour <= 22
    late_night = scenario.hour >= 23 or scenario.hour <= 5

    if evening and scenario.zone_type in {"Commercial", "Mixed", "Market", "Public-Commercial"}:
        recommendations.append(ACTIONS[1])
    if evening and scenario.flexible_load_pct >= 20:
        recommendations.append(ACTIONS[0])
        recommendations.append(ACTIONS[2])
    if scenario.zone_type == "Street Lighting" and late_night:
        recommendations.append(ACTIONS[3])
    if scenario.transformer_load_ratio > 0.8 or stress >= 70:
        recommendations.append(ACTIONS[4])
    if scenario.season in {"Summer", "Festival / Event Day"} and peak_risk >= 55:
        recommendations.append(ACTIONS[5])
    if scenario.critical_load_pct >= 45:
        recommendations.append("Protect critical services; prefer gentle scheduling and monitoring over aggressive interventions")
    if not recommendations:
        recommendations.append(ACTIONS[6])

    unique = []
    for item in recommendations:
        if item not in unique:
            unique.append(item)
    return unique


def safety_guardrails(recommendations: list[str]) -> list[str]:
    banned_terms = ("cutoff", "cut-off", "shutdown", "load shedding", "blackout")
    guarded = []
    for rec in recommendations:
        if any(term in rec.lower() for term in banned_terms):
            continue
        guarded.append(rec)
    return guarded or [ACTIONS[-1]]
