from __future__ import annotations

import pathlib
import sys

import plotly.express as px
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agent import expert_recommendations, fired_rules, safety_guardrails
from app.data_model import SCENARIO_PRESETS, SEASON_FACTORS, ZONE_PROFILES, ZONES, Scenario, hourly_demand_profile, synthetic_zone_table
from app.explainability import explain_agent_choice, explain_scores
from app.forecasting import comfort_disruption_score, estimate_peak_risk, infrastructure_stress_score
from app.optimizer import rank_actions, utility_formula_text


st.set_page_config(page_title="NammaGrid", page_icon="NG", layout="wide")

st.markdown(
    """
    <style>
    .main-header {
        padding: 1.2rem 1.3rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #0f766e 0%, #14532d 100%);
        color: white;
        margin-bottom: 1rem;
    }
    .main-header h1 { margin: 0; font-size: 2.4rem; letter-spacing: 0; }
    .main-header p { margin: .25rem 0 0 0; font-size: 1.05rem; }
    .recommendation-box {
        border: 1px solid #b6e3d4;
        border-left: 6px solid #0f766e;
        border-radius: 8px;
        padding: 1rem;
        background: #f0fdfa;
        margin-bottom: .75rem;
    }
    .small-note { color: #475569; font-size: .92rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="main-header">
        <h1>NammaGrid</h1>
        <p>A Hyperlocal AI Energy Optimisation Agent for Malleshwaram</p>
        <p><strong>Optimize, don't cut off.</strong></p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Demo Controls")
    preset_name = st.selectbox("Scenario preset", list(SCENARIO_PRESETS.keys()))
    preset = SCENARIO_PRESETS[preset_name]
    zone_name = st.selectbox("Local zone", ZONES, index=ZONES.index(preset["zone_name"]))
    default_type = ZONE_PROFILES[zone_name]["zone_type"]
    zone_type = st.selectbox(
        "Zone type",
        ["Residential", "Commercial", "Mixed", "Public-Commercial", "Street Lighting", "Market"],
        index=["Residential", "Commercial", "Mixed", "Public-Commercial", "Street Lighting", "Market"].index(default_type),
    )
    hour = st.slider("Hour", 0, 23, int(preset["hour"]))
    season = st.selectbox("Season", list(SEASON_FACTORS.keys()), index=list(SEASON_FACTORS.keys()).index(preset["season"]))
    estimated_consumers = st.number_input("Estimated consumers", min_value=50, max_value=5000, value=int(preset["estimated_consumers"]), step=50)
    flexible_load_pct = st.slider("Flexible load %", 0, 80, int(preset["flexible_load_pct"]))
    critical_load_pct = st.slider("Critical load %", 0, 90, int(preset["critical_load_pct"]))
    transformer_load_ratio = st.slider("Transformer load ratio", 0.1, 1.25, float(preset["transformer_load_ratio"]), 0.01)
    objective = st.selectbox(
        "Optimisation objective",
        [
            "Balanced local optimisation",
            "Maximise peak reduction",
            "Minimise comfort disruption",
            "Prioritise infrastructure relief",
        ],
        index=[
            "Balanced local optimisation",
            "Maximise peak reduction",
            "Minimise comfort disruption",
            "Prioritise infrastructure relief",
        ].index(preset["objective"]),
    )

scenario = Scenario(
    zone_name=zone_name,
    zone_type=zone_type,
    hour=hour,
    season=season,
    estimated_consumers=int(estimated_consumers),
    flexible_load_pct=float(flexible_load_pct),
    critical_load_pct=float(critical_load_pct),
    transformer_load_ratio=float(transformer_load_ratio),
    objective=objective,
)

peak = estimate_peak_risk(scenario)
stress = infrastructure_stress_score(scenario)
comfort = comfort_disruption_score(scenario)
ranked_actions = rank_actions(scenario, float(peak["score"]), stress)
recommendations = safety_guardrails(expert_recommendations(scenario, float(peak["score"]), stress))
rules = fired_rules(scenario, float(peak["score"]), stress)
demand_profile = hourly_demand_profile(scenario)
zone_table = synthetic_zone_table(season, hour)
top_action = str(ranked_actions.iloc[0]["Action"])
top_score = float(ranked_actions.iloc[0]["Utility score"])
second_action = str(ranked_actions.iloc[1]["Action"])
second_score = float(ranked_actions.iloc[1]["Utility score"])

dashboard_tab, methodology_tab = st.tabs(["Dashboard", "Methodology and Techniques Used"])

with dashboard_tab:
    metric_cols = st.columns(4)
    metric_cols[0].metric("Peak-risk score", f"{peak['score']:.1f}", peak["band"])
    metric_cols[1].metric("Infrastructure stress", f"{stress:.1f}")
    metric_cols[2].metric("Comfort disruption", f"{comfort:.1f}")
    metric_cols[3].metric("Predicted load", f"{peak['load']:.1f} kWh")

    st.markdown("### Agent Recommendation")
    st.markdown(
        f"""
        <div class="recommendation-box">
            <strong>{top_action}</strong><br>
            <span class="small-note">Top utility score: {top_score:.1f}. Safety guardrail: no full electricity cutoffs.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    rec_cols = st.columns([1, 1])
    with rec_cols[0]:
        st.markdown("**Rule-based expert suggestions**")
        for item in recommendations[:4]:
            st.success(item)
    with rec_cols[1]:
        st.markdown("**Rules fired**")
        for rule in rules or ["No high-risk rule fired; normal optimisation mode."]:
            st.write(f"- {rule}")

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### Forecasted Hourly Demand")
        line_chart = px.line(
            demand_profile,
            x="Hour",
            y=["Demand kWh", "Flexible kWh", "Critical kWh"],
            markers=True,
            title=f"{zone_name}",
        )
        line_chart.add_vrect(x0=18, x1=22, fillcolor="red", opacity=0.08, line_width=0)
        line_chart.update_layout(height=390, legend_title_text="Load type")
        st.plotly_chart(line_chart, use_container_width=True)

    with right:
        st.markdown("### Action Utility Scores")
        bar_chart = px.bar(
            ranked_actions,
            x="Utility score",
            y="Action",
            orientation="h",
            color="Utility score",
            color_continuous_scale="Teal",
        )
        bar_chart.update_layout(yaxis={"categoryorder": "total ascending"}, height=390, margin={"l": 10, "r": 10, "t": 40, "b": 20})
        st.plotly_chart(bar_chart, use_container_width=True)

    st.markdown("### Utility Score Breakdown")
    st.caption(utility_formula_text(objective))
    st.dataframe(
        ranked_actions[
            [
                "Action",
                "Peak reduction",
                "Cost saving",
                "Infrastructure relief",
                "Carbon proxy reduction",
                "Comfort penalty",
                "Safety penalty",
                "Rule fit",
                "Utility score",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Why did the agent choose this?")
    explain_cols = st.columns(2)
    with explain_cols[0]:
        for item in explain_agent_choice(scenario, rules, top_action, top_score, second_action, second_score):
            st.write(f"- {item}")
    with explain_cols[1]:
        for item in explain_scores(scenario, float(peak["score"]), stress, comfort):
            st.write(f"- {item}")

    st.markdown("### Zone-Wise Synthetic Malleshwaram Data")
    st.dataframe(zone_table, use_container_width=True, hide_index=True)

    st.markdown("### SDG Alignment")
    sdg_cols = st.columns(4)
    sdg_cols[0].markdown("**SDG 7**\n\nReliable energy access through peak-aware optimisation.")
    sdg_cols[1].markdown("**SDG 11**\n\nNeighbourhood-level infrastructure resilience.")
    sdg_cols[2].markdown("**SDG 12**\n\nResponsible demand shifting instead of wasteful peaks.")
    sdg_cols[3].markdown("**SDG 13**\n\nLower carbon proxy impact from reduced peak pressure.")

with methodology_tab:
    st.markdown("### What problem NammaGrid solves")
    st.write("NammaGrid demonstrates how a local AI agent can reduce electricity peak pressure in Malleshwaram without recommending power cutoffs.")
    st.markdown("### Input parameters")
    st.write("The sidebar controls describe the zone, hour, season, number of consumers, flexible load share, critical load share, transformer load ratio, and optimisation objective.")
    st.markdown("### Synthetic demand data")
    st.write("Each local zone has a profile for residential, commercial, mixed, public, market, or streetlight demand. The model applies morning, daytime, evening, night, and seasonal factors.")
    st.markdown("### Peak-risk and infrastructure stress")
    st.write("Peak risk rises during 18-22, high transformer loading, high critical demand, summer or event days, and night-heavy streetlight loads. Stress uses transformer ratio, critical-load pressure, and public infrastructure baseline.")
    st.markdown("### Agent design")
    st.write("The agent combines a rule-based expert layer with utility-based decision-making. Rules detect known situations; the utility score selects the best safe action.")
    st.markdown("### Forecasting and explainability")
    st.write("The hourly demand chart is a simple forecast built from the selected scenario. The explanation panel reports fired rules, score logic, winning action, and tradeoffs.")
    st.markdown("### SDG alignment")
    st.write("The project supports SDG 7, 11, 12, and 13 by promoting reliable access, resilient cities, responsible consumption, and lower peak-related carbon pressure.")
    st.markdown("### Limitations and real-world path")
    st.write("The data is synthetic and public-data-inspired, so it is not a BESCOM operational tool yet. With feeder, transformer, smart-meter, weather, and event data, this could become a real local planning assistant.")
