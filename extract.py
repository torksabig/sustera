#!/usr/bin/env python3
"""Helsinki large-buildings agent: extract live Ryhti buildings over a GFA threshold.

Default job: municipality 091 (Helsinki), gross_floor_area >= 3000 m².
Drops demolished/destroyed stock and sentinel sizes (>= 500 000 m²).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from codes import code_from_uri, label_for

BUILDING_URL = (
    "https://paikkatiedot.ymparisto.fi/geoserver/ryhti_building"
    "/ogc/features/v1/collections/open_building/items"
)
ADDRESS_URL = (
    "https://paikkatiedot.ymparisto.fi/geoserver/ryhti_building"
    "/ogc/features/v1/collections/open_address/items"
)
USER_AGENT = "helsinki-large-buildings/0.1 (local extract; CC-BY Syke Ryhti)"
PAGE_SIZE = 3000
MAX_RETRIES = 4
DEMOLISHED = {"06", "07", "08"}
SENTINEL_GFA = 500_000
DEFAULT_MIN_SQM = 3000
DEFAULT_MUNICIPALITY = "091"

BUILDING_COLUMNS = [
    "permanent_building_identifier",
    "property_identifier",
    "municipality_number",
    "completion_date",
    "demolition_date",
    "main_purpose_code",
    "main_purpose_fi",
    "usage_status_code",
    "usage_status_fi",
    "heating_method_code",
    "heating_method_fi",
    "heating_energy_source_code",
    "heating_energy_source_fi",
    "facade_material_code",
    "facade_material_fi",
    "load_bearing_material_code",
    "load_bearing_material_fi",
    "construction_method_code",
    "construction_method_fi",
    "volume",
    "number_of_storeys",
    "gross_floor_area",
    "total_area",
    "floor_area",
    "apartment_count",
    "is_accessible",
    "is_protected",
    "lon",
    "lat",
    "building_key",
    "modified_timestamp_utc",
    "voting_district_number",
]

OUT_COLUMNS = [
    "rank_gfa",
    "address_fin",
    "postal_code",
    "postal_office_fin",
    "main_purpose_fi",
    "gross_floor_area",
    "volume",
    "number_of_storeys",
    "apartment_count",
    "heating_method_fi",
    "heating_energy_source_fi",
    "facade_material_fi",
    "load_bearing_material_fi",
    "construction_method_fi",
    "completion_date",
    "usage_status_fi",
    "permanent_building_identifier",
    "property_identifier",
    "lon",
    "lat",
    "building_key",
]

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"


def municipality_code(raw: str) -> str:
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits:
        raise SystemExit(f"Invalid municipality code: {raw!r}")
    return digits.zfill(3)


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(min(2**attempt, 16))
    raise SystemExit(f"Failed to fetch {url}: {last_error}")


def next_page_url(payload: dict) -> str | None:
    for link in payload.get("links") or []:
        if link.get("rel") == "next" and link.get("href"):
            return str(link["href"])
    return None


def collection_url(base: str, municipality: str) -> str:
    query = urllib.parse.urlencode(
        {
            "filter": f"municipality_number='{municipality}'",
            "filter-lang": "cql2-text",
            "limit": str(PAGE_SIZE),
            "f": "application/json",
        }
    )
    return f"{base}?{query}"


def lon_lat(feature: dict) -> tuple[str, str]:
    geom = feature.get("geometry") or {}
    coords = geom.get("coordinates") or []
    if geom.get("type") == "Point" and len(coords) >= 2:
        return str(coords[0]), str(coords[1])
    return "", ""


def clean_date(value: str | None) -> str:
    if not value:
        return ""
    return value.rstrip("Z")


def row_from_feature(feature: dict, municipality: str) -> dict[str, str]:
    props = feature.get("properties") or {}
    lon, lat = lon_lat(feature)
    coded = {
        "main_purpose": props.get("main_purpose"),
        "usage_status": props.get("usage_status"),
        "heating_method": props.get("heating_method"),
        "heating_energy_source": props.get("heating_energy_source"),
        "facade_material": props.get("facade_material"),
        "material_of_load_bearing_structures": props.get("material_of_load_bearing_structures"),
        "construction_method": props.get("construction_method"),
    }
    return {
        "permanent_building_identifier": props.get("permanent_building_identifier") or "",
        "property_identifier": props.get("property_identifier") or "",
        "municipality_number": municipality,
        "completion_date": clean_date(props.get("completion_date")),
        "demolition_date": clean_date(props.get("demolition_date")),
        "main_purpose_code": code_from_uri(coded["main_purpose"]),
        "main_purpose_fi": label_for("main_purpose", coded["main_purpose"]),
        "usage_status_code": code_from_uri(coded["usage_status"]),
        "usage_status_fi": label_for("usage_status", coded["usage_status"]),
        "heating_method_code": code_from_uri(coded["heating_method"]),
        "heating_method_fi": label_for("heating_method", coded["heating_method"]),
        "heating_energy_source_code": code_from_uri(coded["heating_energy_source"]),
        "heating_energy_source_fi": label_for("heating_energy_source", coded["heating_energy_source"]),
        "facade_material_code": code_from_uri(coded["facade_material"]),
        "facade_material_fi": label_for("facade_material", coded["facade_material"]),
        "load_bearing_material_code": code_from_uri(coded["material_of_load_bearing_structures"]),
        "load_bearing_material_fi": label_for(
            "material_of_load_bearing_structures",
            coded["material_of_load_bearing_structures"],
        ),
        "construction_method_code": code_from_uri(coded["construction_method"]),
        "construction_method_fi": label_for("construction_method", coded["construction_method"]),
        "volume": "" if props.get("volume") is None else str(props.get("volume")),
        "number_of_storeys": "" if props.get("number_of_storeys") is None else str(props.get("number_of_storeys")),
        "gross_floor_area": "" if props.get("gross_floor_area") is None else str(props.get("gross_floor_area")),
        "total_area": "" if props.get("total_area") is None else str(props.get("total_area")),
        "floor_area": "" if props.get("floor_area") is None else str(props.get("floor_area")),
        "apartment_count": "" if props.get("apartment_count") is None else str(props.get("apartment_count")),
        "is_accessible": "" if props.get("is_accessible") is None else str(props.get("is_accessible")),
        "is_protected": "" if props.get("is_protected") is None else str(props.get("is_protected")),
        "lon": lon,
        "lat": lat,
        "building_key": props.get("building_key") or "",
        "modified_timestamp_utc": props.get("modified_timestamp_utc") or "",
        "voting_district_number": props.get("voting_district_number") or "",
    }


def to_float(value: str | None) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def keep_building(row: dict[str, str], min_sqm: float) -> bool:
    if row.get("usage_status_code") in DEMOLISHED:
        return False
    gfa = to_float(row.get("gross_floor_area", ""))
    if gfa is None or gfa < min_sqm or gfa >= SENTINEL_GFA:
        return False
    return True


def fetch_collection(url: str | None, label: str) -> list[dict]:
    rows: list[dict] = []
    page = 0
    print(f"Fetching {label}…", flush=True)
    while url:
        page += 1
        payload = get_json(url)
        features = payload.get("features") or []
        rows.extend(features)
        print(f"  {label} page {page}: +{len(features)} (total {len(rows)})", flush=True)
        url = next_page_url(payload)
    return rows


def load_or_fetch_buildings(
    municipality: str,
    path: Path,
    fetch: bool,
) -> list[dict[str, str]]:
    if path.exists() and not fetch:
        print(f"Reading buildings from {path}", flush=True)
        with path.open(encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    features = fetch_collection(collection_url(BUILDING_URL, municipality), "buildings")
    rows = [row_from_feature(feature, municipality) for feature in features]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BUILDING_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Cached {len(rows)} buildings → {path}", flush=True)
    return rows


def load_or_fetch_addresses(
    municipality: str,
    path: Path,
    fetch: bool,
) -> dict[str, list[dict[str, str]]]:
    by_building: dict[str, list[dict[str, str]]] = defaultdict(list)
    if path.exists() and not fetch:
        print(f"Reading addresses from {path}", flush=True)
        with path.open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = row.get("building_key") or ""
                if key:
                    by_building[key].append(row)
        return by_building

    features = fetch_collection(collection_url(ADDRESS_URL, municipality), "addresses")
    rows: list[dict[str, str]] = []
    for feature in features:
        props = feature.get("properties") or {}
        row = {
            "building_key": props.get("building_key") or "",
            "address_fin": props.get("address_fin") or "",
            "postal_code": props.get("postal_code") or "",
            "postal_office_fin": props.get("postal_office_fin") or "",
        }
        rows.append(row)
        if row["building_key"]:
            by_building[row["building_key"]].append(row)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["building_key", "address_fin", "postal_code", "postal_office_fin"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Cached {len(rows)} addresses → {path}", flush=True)
    return by_building


def attach_address(row: dict[str, str], addresses: list[dict[str, str]]) -> dict[str, str]:
    unique_addr: list[str] = []
    seen: set[str] = set()
    postal_code = ""
    postal_office = ""
    for item in addresses:
        text = (item.get("address_fin") or "").strip()
        if text and text not in seen:
            seen.add(text)
            unique_addr.append(text)
        postal_code = postal_code or (item.get("postal_code") or "")
        postal_office = postal_office or (item.get("postal_office_fin") or "")
    return {
        **row,
        "address_fin": " | ".join(unique_addr),
        "postal_code": postal_code,
        "postal_office_fin": postal_office,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--municipality", default=DEFAULT_MUNICIPALITY)
    parser.add_argument("--min-sqm", type=float, default=DEFAULT_MIN_SQM)
    parser.add_argument("--buildings", type=Path, default=None)
    parser.add_argument("--addresses", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Ignore local caches and page the live Ryhti API",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    municipality = municipality_code(args.municipality)
    min_sqm = float(args.min_sqm)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    buildings_path = args.buildings or CACHE_DIR / f"open_buildings_{municipality}.csv"
    addresses_path = args.addresses or CACHE_DIR / f"open_addresses_{municipality}.csv"
    out_csv = args.out or DATA_DIR / "helsinki_buildings_over_3000sqm.csv"
    if municipality != DEFAULT_MUNICIPALITY or min_sqm != DEFAULT_MIN_SQM:
        out_csv = args.out or DATA_DIR / f"buildings_{municipality}_over_{int(min_sqm)}sqm.csv"

    buildings = load_or_fetch_buildings(municipality, buildings_path, args.fetch)
    kept = [row for row in buildings if keep_building(row, min_sqm)]
    kept.sort(key=lambda r: to_float(r.get("gross_floor_area", "")) or 0, reverse=True)

    by_building = load_or_fetch_addresses(municipality, addresses_path, args.fetch)
    out_rows: list[dict[str, str]] = []
    for index, row in enumerate(kept, start=1):
        joined = attach_address(row, by_building.get(row.get("building_key") or "", []))
        joined["rank_gfa"] = str(index)
        out_rows.append({col: joined.get(col, "") for col in OUT_COLUMNS})

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUT_COLUMNS)
        writer.writeheader()
        writer.writerows(out_rows)

    gfas = [to_float(row["gross_floor_area"]) or 0 for row in out_rows]
    summary = {
        "job": f"live buildings in municipality {municipality} with gross_floor_area >= {min_sqm} m2",
        "municipality_number": municipality,
        "min_sqm": min_sqm,
        "scanned_buildings": len(buildings),
        "kept_buildings": len(out_rows),
        "with_address": sum(1 for row in out_rows if row["address_fin"]),
        "gfa_min": min(gfas) if gfas else None,
        "gfa_max": max(gfas) if gfas else None,
        "gfa_sum": round(sum(gfas), 1) if gfas else 0,
        "excluded": "demolished/destroyed (06/07/08), GFA>=500000",
        "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": BUILDING_URL,
        "license": "CC BY 4.0 (Syke / Ryhti)",
        "main_purpose_fi": dict(Counter(row["main_purpose_fi"] for row in out_rows).most_common()),
        "heating_energy_source_fi": dict(
            Counter(row["heating_energy_source_fi"] or "(tyhjä)" for row in out_rows).most_common()
        ),
        "heating_method_fi": dict(
            Counter(row["heating_method_fi"] or "(tyhjä)" for row in out_rows).most_common()
        ),
        "top10_by_gfa": [
            {
                "rank": row["rank_gfa"],
                "address_fin": row["address_fin"],
                "gross_floor_area": row["gross_floor_area"],
                "volume": row["volume"],
                "main_purpose_fi": row["main_purpose_fi"],
            }
            for row in out_rows[:10]
        ],
    }
    out_json = out_csv.with_suffix(".summary.json")
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Scanned {len(buildings)} buildings; kept {len(out_rows)} with GFA >= {min_sqm} m²")
    print(f"Addresses on {summary['with_address']} / {len(out_rows)}")
    print(f"Wrote {out_csv}")
    print(f"Summary → {out_json}")
    if not out_rows:
        sys.exit(1)


if __name__ == "__main__":
    main()
