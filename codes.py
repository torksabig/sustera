"""Finnish labels for Ryhti / Suomi.fi building code lists.

Values are the trailing code in URIs such as
http://uri.suomi.fi/codelist/rytj/lammitystapa/code/03
"""

from __future__ import annotations

HEATING_METHOD: dict[str, str] = {
    "01": "Vesikeskuslämmitys",
    "02": "Ilmakeskuslämmitys",
    "03": "Sähkölämmitys",
    "04": "Uuni-takka-kamiinalämmitys",
    "05": "Aurinkolämmitys",
    "06": "Ilmalämpöpumppu",
    "07": "Ei kiinteää lämmityslaitetta",
    "99": "Muu",
}

HEATING_ENERGY_SOURCE: dict[str, str] = {
    "01": "Kauko- tai aluelämpö",
    "02": "Kevyt polttoöljy",
    "03": "Raskas polttoöljy",
    "04": "Sähkö",
    "05": "Kaasu",
    "06": "Kivihiili",
    "07": "Puu",
    "08": "Turve",
    "09": "Maalämpö tms.",
    "10": "Aurinkoenergia",
    "11": "Lämpöpumppu",
    "1101": "Maalämpöpumppu",
    "1102": "Ilmalämpöpumppu",
    "1103": "Poistoilmalämpöpumppu",
    "1104": "Ilma-vesilämpöpumppu",
    "99": "Muu",
}

FACADE_MATERIAL: dict[str, str] = {
    "00": "Ei tiedossa",
    "01": "Betoni",
    "02": "Tiili",
    "03": "Metallilevy",
    "04": "Kivi",
    "05": "Puu",
    "06": "Lasi",
    "99": "Muu",
}

LOAD_BEARING_MATERIAL: dict[str, str] = {
    "00": "Ei tiedossa",
    "01": "Betoni",
    "02": "Tiili",
    "03": "Teräs",
    "04": "Puu",
    "99": "Muu",
}

MAIN_PURPOSE: dict[str, str] = {
    "01": "Vapaa-ajan asuinrakennus",
    "02": "Toimisto-, tuotanto-, yhdyskuntatekniikan tai muut rakennukset",
    "03": "Talousrakennus",
    "04": "Saunarakennus",
    "05": "Pientalo",
    "06": "Kerrostalo",
    "07": "Julkinen rakennus",
}

USAGE_STATUS: dict[str, str] = {
    "01": "Käytetään vakinaiseen asumiseen",
    "02": "Toimitila- tai tuotantokäytössä",
    "03": "Käytetään loma-asumiseen",
    "04": "Käytetään muuhun tilapäiseen asumiseen",
    "05": "Tyhjillään",
    "06": "Purettu uudisrakentamisen vuoksi",
    "07": "Purettu muusta syystä",
    "08": "Tuhoutunut",
    "09": "Ränsistymisen vuoksi hylätty",
    "10": "Käytöstä ei ole tietoa",
    "11": "Muu (sauna, liiteri, kellotapuli, yms.)",
}

CONSTRUCTION_METHOD: dict[str, str] = {
    "01": "Elementti",
    "02": "Paikalla tehty",
}

FIELD_CODELISTS: dict[str, dict[str, str]] = {
    "heating_method": HEATING_METHOD,
    "heating_energy_source": HEATING_ENERGY_SOURCE,
    "facade_material": FACADE_MATERIAL,
    "material_of_load_bearing_structures": LOAD_BEARING_MATERIAL,
    "main_purpose": MAIN_PURPOSE,
    "usage_status": USAGE_STATUS,
    "construction_method": CONSTRUCTION_METHOD,
}


def code_from_uri(value: str | None) -> str:
    if not value:
        return ""
    text = value.strip()
    if "/code/" in text:
        return text.rsplit("/code/", 1)[-1].strip()
    return text


def label_for(field: str, value: str | None) -> str:
    code = code_from_uri(value)
    if not code:
        return ""
    table = FIELD_CODELISTS.get(field, {})
    return table.get(code, code)
