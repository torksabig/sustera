# Helsinki large buildings

Cursor agent + extractor for **every live Helsinki building over 3000 m²** in Syke Ryhti.

Municipality `091`. Source: [Ryhti OGC API Features](https://paikkatiedot.ymparisto.fi/geoserver/ryhti_building/ogc/features/v1) (`open_building` + `open_address`), CC BY 4.0.

This pipeline is **not** joined to weather, spot prices, or energy-usage series.

## Agent

Project subagent: `.cursor/agents/helsinki-buildings-extractor.md`.

Ask it to extract Helsinki buildings ≥ 3000 m². It runs `extract.py` and reports the CSV.

## Run

```bash
python3 extract.py
```

Defaults: Helsinki `091`, threshold 3000 m². Reuses `data/cache/` when present; otherwise pages the live API.

```bash
python3 extract.py --fetch
python3 extract.py --min-sqm 3000 --buildings /path/to/open_buildings_091.csv --addresses /path/to/open_addresses_091.csv
```

## Output

| File | What |
| --- | --- |
| `data/helsinki_buildings_over_3000sqm.csv` | Ranked extract with addresses, heating, materials, structures |
| `data/helsinki_buildings_over_3000sqm.summary.json` | Counts, purpose mix, top 10 by GFA |

Dropped: demolished/destroyed (`06`/`07`/`08`) and sentinel GFA ≥ 500 000 m².

## License of data

Ryhti open building and address layers are CC BY 4.0 (Syke / Ryhti). Credit Syke when redistributing extracts.
