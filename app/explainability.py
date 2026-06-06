from __future__ import annotations

from app.data_model import Scenario


def explain_scores(scenario: Scenario, peak_risk: float, stress: float, comfort: float) -> list[str]:
    explanations = []
    if 18 <= scenario.hour <= 22:
        explanations.append("Evening hours from 18 to 22 raise peak-risk because homes, markets, lighting, and cooling overlap.")
    else:
        explanations.append("The selected hour is outside the main evening peak window, so risk is driven more by local load mix.")

    if scenario.transformer_load_ratio > 0.8:
        explanations.append("Transformer load ratio is above 0.8, so monitoring and maintenance priority receive extra weight.")
    else:
        explanations.append("Transformer load ratio is below the high-stress threshold, reducing infrastructure urgency.")

    if scenario.zone_type in {"Commercial", "Mixed", "Market", "Public-Commercial"} and 18 <= scenario.hour <= 22:
        explanations.append("Commercial or mixed evening demand makes staggered cooling and lighting a high-value action.")

    if scenario.zone_type == "Street Lighting":
        explanations.append("Street-lighting actions use adaptive dimming after low-footfall hours, never a full shutoff.")

    if scenario.critical_load_pct >= 45:
        explanations.append("High critical load limits aggressive interventions and protects essential services.")

    explanations.append(f"Peak risk is {peak_risk:.1f}, infrastructure stress is {stress:.1f}, and comfort disruption is {comfort:.1f}.")
    return explanations


def explain_agent_choice(
    scenario: Scenario,
    fired_rules: list[str],
    top_action: str,
    top_score: float,
    second_action: str,
    second_score: float,
) -> list[str]:
    margin = round(top_score - second_score, 1)
    return [
        f"Rules fired: {len(fired_rules)} rule(s) matched this scenario, so the agent is not using a random suggestion.",
        f"Winning action: {top_action} scored {top_score:.1f}, ahead of {second_action} by {margin:.1f} utility points.",
        "Utility scores combine benefits from peak reduction, cost saving, infrastructure relief, and carbon proxy reduction.",
        "Comfort disruption and safety risk are subtracted, so actions that disturb people or critical services are pushed down.",
        "Cutoffs are avoided because the project constraint is to optimise flexible demand and protect essential electricity access.",
    ]
