from __future__ import annotations

from app.data_model import Scenario, demand_components, predicted_load_kwh


def estimate_peak_risk(scenario: Scenario) -> dict[str, float | str]:
    load = predicted_load_kwh(scenario)
    components = demand_components(scenario.zone_name, scenario.hour, scenario.season, scenario.estimated_consumers)
    evening_boost = 26 if 18 <= scenario.hour <= 22 else 0
    night_streetlight_boost = 14 if scenario.zone_type == "Street Lighting" and (scenario.hour >= 23 or scenario.hour <= 5) else 0
    transformer_proxy = max(float(components["transformer_ratio"]), scenario.transformer_load_ratio)
    transformer_boost = max(transformer_proxy - 0.70, 0) * 95
    season_boost = 12 if scenario.season in {"Summer", "Festival / Event Day"} else 4
    flexible_relief = scenario.flexible_load_pct * 0.16
    critical_constraint = scenario.critical_load_pct * 0.12

    score = 28 + evening_boost + night_streetlight_boost + transformer_boost + season_boost - flexible_relief + critical_constraint
    score = max(0, min(100, round(score, 1)))

    if score >= 75:
        band = "High"
    elif score >= 50:
        band = "Moderate"
    else:
        band = "Low"

    return {"score": score, "band": band, "load": round(load, 1), "transformer_proxy": round(transformer_proxy, 2)}


def infrastructure_stress_score(scenario: Scenario) -> float:
    components = demand_components(scenario.zone_name, scenario.hour, scenario.season, scenario.estimated_consumers)
    transformer_proxy = max(float(components["transformer_ratio"]), scenario.transformer_load_ratio)
    evening = 10 if 18 <= scenario.hour <= 22 else 0
    public_baseline = 7 if scenario.zone_type in {"Public-Commercial", "Street Lighting", "Market"} else 2
    score = (transformer_proxy * 72) + evening + public_baseline + (scenario.critical_load_pct * 0.14)
    return round(max(0, min(100, score)), 1)


def comfort_disruption_score(scenario: Scenario) -> float:
    flexible_pressure = max(0, 35 - scenario.flexible_load_pct) * 0.7
    critical_pressure = scenario.critical_load_pct * 0.45
    evening_penalty = 8 if 18 <= scenario.hour <= 22 else 0
    return round(max(0, min(100, flexible_pressure + critical_pressure + evening_penalty)), 1)
