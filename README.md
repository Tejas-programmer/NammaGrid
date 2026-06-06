# NammaGrid

**Motto:** Optimize, don't cut off.

NammaGrid is a Streamlit Intro to AI project that demonstrates a hyperlocal electricity optimisation agent for Malleshwaram, Bengaluru. It estimates local demand, scores peak-risk, identifies transformer stress, ranks safe optimisation actions, and explains why the agent chose its recommendation.

## Problem Statement

Neighbourhood electricity peaks happen when residential evening usage, market activity, commercial cooling, street lighting, and public infrastructure demand overlap. A useful local agent should reduce stress without recommending disruptive cutoffs.

## Solution

The app provides scenario presets and manual controls for zone, hour, season, consumers, flexible load, critical load, transformer ratio, and optimisation objective. It generates synthetic Malleshwaram demand patterns, forecasts hourly load, fires expert rules, and ranks possible actions using a visible utility score.

## AI Methodology

- **Synthetic demand model:** local zone profiles capture residential evening peaks, commercial activity, mixed-zone overlap, streetlight night load, public baseline demand, flexible load, critical load, and transformer stress proxy.
- **Demand estimation:** the app estimates hourly demand from time-of-day, season, consumer count, and zone profile.
- **Rule-based expert layer:** rules detect evening peak, commercial/mixed evening demand, streetlight night load, high transformer stress, high critical load, and low-risk conditions.
- **Utility-based agent:** actions are scored by peak reduction, cost saving, infrastructure relief, carbon proxy reduction, comfort disruption penalty, and safety risk penalty.
- **Constraint handling:** the agent is constrained to avoid full power cutoffs and to protect critical loads.
- **Explainability:** the dashboard shows fired rules, score meaning, winning action, tradeoff, and why cutoffs are avoided.

## SDG Alignment

- **SDG 7:** supports reliable and cleaner energy access.
- **SDG 11:** improves local urban infrastructure resilience.
- **SDG 12:** encourages responsible electricity consumption through demand shifting.
- **SDG 13:** reduces peak-related carbon proxy pressure.

## How to Run

```cmd
.venv\Scripts\python.exe -m streamlit run app\main.py
```

## Project Structure

```text
NammaGrid/
  app/
    main.py
    data_model.py
    agent.py
    optimizer.py
    forecasting.py
    explainability.py
  data/
    raw/
    processed/
  assets/
  docs/
  reports/
  README.md
  requirements.txt
  .gitignore
```

## Limitations

This is a student demo using synthetic and public-data-inspired assumptions, not live BESCOM operational data. The results should be treated as explanatory and educational, not as grid-control instructions.

## Future Scope

- Connect live BESCOM or smart-meter data
- Add weather and event signals for better forecasting
- Include ward-level transformer health history
- Add household and shopkeeper feedback loops
- Export optimisation reports for local planners
