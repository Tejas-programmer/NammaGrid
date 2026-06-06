from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


ZONES = [
    "8th Cross Residential Pocket",
    "Sampige Road Commercial Belt",
    "15th Cross Mixed Zone",
    "Margosa Road Public-Commercial Edge",
    "Temple Street Lighting Corridor",
    "Malleshwaram Market Cluster",
]


ZONE_PROFILES = {
    "8th Cross Residential Pocket": {
        "zone_type": "Residential",
        "base_kw": 390,
        "morning_lift": 0.18,
        "day_lift": 0.05,
        "evening_lift": 0.58,
        "night_lift": -0.18,
        "critical_load": 0.18,
        "flexible_load": 0.38,
        "transformer_capacity_kw": 780,
        "public_baseline_kw": 22,
    },
    "Sampige Road Commercial Belt": {
        "zone_type": "Commercial",
        "base_kw": 650,
        "morning_lift": 0.16,
        "day_lift": 0.48,
        "evening_lift": 0.36,
        "night_lift": -0.28,
        "critical_load": 0.22,
        "flexible_load": 0.30,
        "transformer_capacity_kw": 920,
        "public_baseline_kw": 42,
    },
    "15th Cross Mixed Zone": {
        "zone_type": "Mixed",
        "base_kw": 540,
        "morning_lift": 0.20,
        "day_lift": 0.28,
        "evening_lift": 0.48,
        "night_lift": -0.18,
        "critical_load": 0.24,
        "flexible_load": 0.33,
        "transformer_capacity_kw": 840,
        "public_baseline_kw": 35,
    },
    "Margosa Road Public-Commercial Edge": {
        "zone_type": "Public-Commercial",
        "base_kw": 520,
        "morning_lift": 0.18,
        "day_lift": 0.34,
        "evening_lift": 0.33,
        "night_lift": 0.02,
        "critical_load": 0.35,
        "flexible_load": 0.18,
        "transformer_capacity_kw": 760,
        "public_baseline_kw": 90,
    },
    "Temple Street Lighting Corridor": {
        "zone_type": "Street Lighting",
        "base_kw": 230,
        "morning_lift": -0.20,
        "day_lift": -0.36,
        "evening_lift": 0.72,
        "night_lift": 0.44,
        "critical_load": 0.46,
        "flexible_load": 0.16,
        "transformer_capacity_kw": 520,
        "public_baseline_kw": 80,
    },
    "Malleshwaram Market Cluster": {
        "zone_type": "Market",
        "base_kw": 710,
        "morning_lift": 0.22,
        "day_lift": 0.46,
        "evening_lift": 0.42,
        "night_lift": -0.30,
        "critical_load": 0.30,
        "flexible_load": 0.26,
        "transformer_capacity_kw": 940,
        "public_baseline_kw": 55,
    },
}


SEASON_FACTORS = {
    "Summer": 1.18,
    "Monsoon": 1.04,
    "Winter": 0.94,
    "Festival / Event Day": 1.28,
}


SCENARIO_PRESETS = {
    "Evening residential peak": {
        "zone_name": "8th Cross Residential Pocket",
        "hour": 20,
        "season": "Summer",
        "estimated_consumers": 1150,
        "flexible_load_pct": 42,
        "critical_load_pct": 20,
        "transformer_load_ratio": 0.84,
        "objective": "Maximise peak reduction",
    },
    "Commercial market load": {
        "zone_name": "Malleshwaram Market Cluster",
        "hour": 18,
        "season": "Festival / Event Day",
        "estimated_consumers": 1650,
        "flexible_load_pct": 27,
        "critical_load_pct": 31,
        "transformer_load_ratio": 0.88,
        "objective": "Balanced local optimisation",
    },
    "Streetlight night optimisation": {
        "zone_name": "Temple Street Lighting Corridor",
        "hour": 23,
        "season": "Winter",
        "estimated_consumers": 450,
        "flexible_load_pct": 16,
        "critical_load_pct": 48,
        "transformer_load_ratio": 0.63,
        "objective": "Minimise comfort disruption",
    },
    "High transformer stress": {
        "zone_name": "Margosa Road Public-Commercial Edge",
        "hour": 19,
        "season": "Summer",
        "estimated_consumers": 1400,
        "flexible_load_pct": 19,
        "critical_load_pct": 43,
        "transformer_load_ratio": 1.05,
        "objective": "Prioritise infrastructure relief",
    },
    "Low-risk normal day": {
        "zone_name": "15th Cross Mixed Zone",
        "hour": 11,
        "season": "Monsoon",
        "estimated_consumers": 650,
        "flexible_load_pct": 35,
        "critical_load_pct": 24,
        "transformer_load_ratio": 0.56,
        "objective": "Balanced local optimisation",
    },
}


@dataclass(frozen=True)
class Scenario:
    zone_name: str
    zone_type: str
    hour: int
    season: str
    estimated_consumers: int
    flexible_load_pct: float
    critical_load_pct: float
    transformer_load_ratio: float
    objective: str


def hour_factor(hour: int, zone_type: str) -> float:
    profile = next((item for item in ZONE_PROFILES.values() if item["zone_type"] == zone_type), None)
    if profile is None:
        profile = ZONE_PROFILES["15th Cross Mixed Zone"]

    factor = 1.0
    if 6 <= hour <= 9:
        factor += float(profile["morning_lift"])
    if 10 <= hour <= 17:
        factor += float(profile["day_lift"])
    if 18 <= hour <= 22:
        factor += float(profile["evening_lift"])
    if hour >= 23 or hour <= 5:
        factor += float(profile["night_lift"])
    return max(factor, 0.55)


def demand_components(zone_name: str, hour: int, season: str, estimated_consumers: int | None = None) -> dict[str, float]:
    profile = ZONE_PROFILES[zone_name]
    load_factor = hour_factor(hour, profile["zone_type"]) * SEASON_FACTORS[season]
    consumer_factor = 1.0 if estimated_consumers is None else 0.72 + min(estimated_consumers, 3000) / 2600
    total_load = (float(profile["base_kw"]) * load_factor * consumer_factor) + float(profile["public_baseline_kw"])
    critical = total_load * float(profile["critical_load"])
    flexible = total_load * float(profile["flexible_load"])
    baseline = max(total_load - critical - flexible, 0)
    transformer_ratio = total_load / float(profile["transformer_capacity_kw"])
    return {
        "total_load": round(total_load, 1),
        "critical_load": round(critical, 1),
        "flexible_load": round(flexible, 1),
        "baseline_load": round(baseline, 1),
        "transformer_ratio": round(min(transformer_ratio, 1.35), 2),
    }


def synthetic_zone_table(season: str, hour: int) -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(42)
    for zone in ZONES:
        profile = ZONE_PROFILES[zone]
        noise = float(rng.normal(0, 0.025))
        components = demand_components(zone, hour, season)
        predicted_kw = round(components["total_load"] * (1 + noise), 1)
        rows.append(
            {
                "Zone": zone,
                "Type": profile["zone_type"],
                "Predicted load kWh": predicted_kw,
                "Flexible kWh": round(components["flexible_load"], 1),
                "Critical kWh": round(components["critical_load"], 1),
                "Flexible load %": round(profile["flexible_load"] * 100, 1),
                "Critical load %": round(profile["critical_load"] * 100, 1),
                "Transformer stress proxy": round(min(predicted_kw / float(profile["transformer_capacity_kw"]), 1.35), 2),
            }
        )
    return pd.DataFrame(rows)


def hourly_demand_profile(scenario: Scenario) -> pd.DataFrame:
    profile = ZONE_PROFILES[scenario.zone_name]
    rows = []
    for hour in range(24):
        components = demand_components(scenario.zone_name, hour, scenario.season, scenario.estimated_consumers)
        rows.append(
            {
                "Hour": hour,
                "Demand kWh": components["total_load"],
                "Flexible kWh": components["flexible_load"],
                "Critical kWh": components["critical_load"],
                "Baseline kWh": components["baseline_load"],
            }
        )
    return pd.DataFrame(rows)


def predicted_load_kwh(scenario: Scenario) -> float:
    table = hourly_demand_profile(scenario)
    return float(table.loc[table["Hour"] == scenario.hour, "Demand kWh"].iloc[0])
