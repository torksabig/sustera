# Helsinki large-buildings agent

When this repo is the workspace, extract Helsinki buildings automatically.

## Default job

From the repository root, with no extra questions:

```bash
python3 agent.py
```

That live-fetches Syke Ryhti (`open_building` + `open_address`) for municipality `091` and writes every live building with gross floor area ≥ 3000 m² to:

- `data/helsinki_buildings_over_3000sqm.csv`
- `data/helsinki_buildings_over_3000sqm.summary.json`

Do not join weather, spot, or usage series. Do not commit `data/cache/`. Credit Syke / Ryhti, CC BY 4.0.

Project subagent: `.cursor/agents/helsinki-buildings-extractor.md`.
