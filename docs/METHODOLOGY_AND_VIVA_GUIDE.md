# NammaGrid Methodology and Viva Guide

## 2-Minute Project Explanation

NammaGrid is a Streamlit-based AI demo for hyperlocal electricity optimisation in Malleshwaram, Bengaluru. The project models local electricity demand for different neighbourhood zones, estimates peak-risk and infrastructure stress, and recommends safe optimisation actions. The motto is "Optimize, don't cut off" because the goal is to reduce peak pressure without suggesting power shutdowns or load shedding.

The app uses synthetic demand data inspired by real local patterns: residential evening peaks, market and commercial activity, mixed-zone overlap, streetlight night load, and public infrastructure baseline demand. A rule-based expert layer detects scenario conditions, and a utility-based agent ranks actions by peak reduction, cost saving, infrastructure relief, carbon proxy reduction, comfort disruption penalty, and safety risk penalty.

## PEAS Description

- **Performance measure:** lower peak-risk, lower transformer stress, lower comfort disruption, safer recommendations, better SDG alignment.
- **Environment:** Malleshwaram zones such as residential pockets, commercial belts, market clusters, mixed roads, public-commercial edges, and street lighting corridors.
- **Actuators:** recommend demand shifting, staggered loads, pump scheduling, adaptive streetlight dimming, transformer monitoring, solar or battery buffering, or no aggressive intervention.
- **Sensors:** selected hour, season, zone type, estimated consumers, flexible load percentage, critical load percentage, transformer load ratio, and optimisation objective.

## Agent Type

The agent is a utility-based decision-making agent with a rule-based expert layer.

The expert layer identifies important conditions such as evening peak, commercial evening demand, streetlight night load, high transformer stress, high critical load, and low-risk conditions. The utility layer then scores possible actions and selects the most useful safe action.

## AI Techniques Used

- Synthetic data modelling
- Demand estimation and simple forecasting
- Rule-based expert system
- Utility-based action selection
- Constraint handling through safety and comfort penalties
- Explainable AI-style reasoning panel

## Why This Is Better Than a Generic Electricity Saver

Generic electricity-saving advice usually gives broad tips like "turn off lights." NammaGrid is local and scenario-aware. It changes recommendations based on the zone, hour, season, transformer stress, critical load, and flexible load. It also avoids unsafe or disruptive advice.

## Why "Optimize, Don't Cut Off" Matters

Electricity access affects comfort, safety, business activity, street lighting, healthcare, and public services. The project treats electricity as an essential service. Instead of recommending cutoffs, it recommends softer actions such as shifting flexible demand, dimming streetlights only after low-footfall hours, and improving transformer monitoring.

## Major Module/File Explanation

- `app/main.py`: Streamlit interface, sidebar presets, dashboard, charts, recommendation panel, and methodology section.
- `app/data_model.py`: Zone profiles, scenario presets, synthetic demand generation, load components, and hourly demand estimation.
- `app/forecasting.py`: Peak-risk score, infrastructure stress score, comfort disruption score, and predicted load estimate.
- `app/agent.py`: Rule-based expert layer, fired rules, recommendation list, and safety guardrails.
- `app/optimizer.py`: Available actions, utility score formula, objective weighting, and ranked action table.
- `app/explainability.py`: Student-friendly explanation text for fired rules, utility scores, tradeoffs, and cutoff avoidance.
- `README.md`: Project overview, run command, methodology summary, structure, limitations, and future scope.
- `docs/METHODOLOGY_AND_VIVA_GUIDE.md`: Viva-ready project explanation, PEAS, AI techniques, Q&A, and demo flow.

## Likely Viva Questions and Answers

**Q: What problem does NammaGrid solve?**  
A: It helps reduce neighbourhood peak electricity stress by recommending safe local optimisation actions instead of power cutoffs.

**Q: What type of AI agent is this?**  
A: It is a utility-based agent with a rule-based expert layer.

**Q: What are the inputs?**  
A: Zone type, hour, season, estimated consumers, flexible load percentage, critical load percentage, transformer load ratio, and optimisation objective.

**Q: What is the utility function?**  
A: It combines peak reduction, cost saving, infrastructure relief, and carbon proxy reduction, then subtracts comfort disruption and safety risk penalties.

**Q: Why is a rule-based layer needed?**  
A: It makes the agent understandable and ensures local expert conditions, such as evening peak or high transformer stress, are explicitly considered.

**Q: How does the app handle streetlights?**  
A: It recommends adaptive dimming after low-footfall hours, not turning streetlights off.

**Q: Why does the project avoid power cutoffs?**  
A: Cutoffs can harm safety, comfort, business, and critical services. The project focuses on optimisation and access protection.

**Q: Is the data real?**  
A: No. It is synthetic and public-data-inspired for a student demo. Real deployment would need BESCOM feeder, transformer, smart-meter, weather, and event data.

**Q: How is forecasting used?**  
A: The app estimates hourly demand based on local zone profiles, time of day, season, and consumer count.

**Q: What SDGs are aligned?**  
A: SDG 7, SDG 11, SDG 12, and SDG 13.

## Demo Flow Step-by-Step

1. Open the app with `.venv\Scripts\python.exe -m streamlit run app\main.py`.
2. Start with the "Evening residential peak" preset.
3. Explain the four metrics: peak-risk, infrastructure stress, comfort disruption, and predicted load.
4. Show the "Agent Recommendation" panel and the fired rules.
5. Show the hourly demand chart and point out the evening peak window.
6. Show the action utility bar chart and explain that higher utility means better overall tradeoff.
7. Open "Why did the agent choose this?" and explain the winning action and cutoff avoidance.
8. Switch to "Streetlight night optimisation" and explain adaptive dimming.
9. Switch to "High transformer stress" and explain monitoring/maintenance priority.
10. Open the methodology tab and summarize how the AI logic works.
