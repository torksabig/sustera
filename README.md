# Helsinki large buildings

## Sustera file (GitHub)

- [`sustera.csv`](sustera.csv) — HQ, occupied offices, named technical-management sites, Helsinki Ryhti matches
- [`sustera.json`](sustera.json) — same records plus sources

Unattended agent that extracts **every live Helsinki building over 3000 m²** from Syke Ryhti.

Municipality `091`. Source: [Ryhti OGC API Features](https://paikkatiedot.ymparisto.fi/geoserver/ryhti_building/ogc/features/v1) (`open_building` + `open_address`), CC BY 4.0.

This pipeline is **not** joined to weather, spot prices, or energy-usage series.

## Agent

`python3 agent.py` always live-fetches. No prompts.

Cursor subagent: `.cursor/agents/helsinki-buildings-extractor.md` (also installed user-wide). Mention Helsinki buildings / extract / Ryhti and it should run on its own.

Daily 06:00 local via launchd:

```bash
chmod +x install-schedule.sh
./install-schedule.sh
```

## Run

```bash
python3 agent.py          # live fetch (agent)
python3 extract.py        # reuse data/cache/ if present
python3 extract.py --fetch
```

## Output

| File | What |
| --- | --- |
| `data/helsinki_buildings_over_3000sqm.csv` | Ranked extract with addresses, heating, materials, structures |
| `data/helsinki_buildings_over_3000sqm.summary.json` | Counts, purpose mix, top 10 by GFA |

Dropped: demolished/destroyed (`06`/`07`/`08`) and sentinel GFA ≥ 500 000 m².

## License of data

Ryhti open building and address layers are CC BY 4.0 (Syke / Ryhti). Credit Syke when redistributing extracts.
