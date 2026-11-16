"""Pre-integration data quality profile for the three raw source files.

Reads the raw files in data/raw/ without modifying them and writes:
  outputs/quality/pre_integration_profile.json  (machine-readable results)
  outputs/quality/pre_integration_profile.md    (human-readable report)

The checks are grouped by the four quality dimensions required by the
course: accuracy, completeness, timeliness, and consistency. A final
section checks whether the three sources can be joined on county FIPS.

Run from anywhere:  python src/profile_sources.py
"""

import io
import json
import re
import zipfile
from pathlib import Path

import pandas as pd

# All paths are relative to the repository root, so the script works on any machine.
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs" / "quality"

USDA_ZIP = RAW / "food_environment_atlas_2025.zip"
USDA_MEMBER = "StateAndCountyData.csv"
USDA_README = "ReadMeFile2025.txt"
CENSUS_CSV = RAW / "co-est2024-alldata.csv"
PLACES_CSV = RAW / "places_county_2024.csv"

FIPS_PATTERN = re.compile(r"^\d{5}$")
USDA_SENTINELS = {"-9999": "not available / suppressed", "-8888": "county did not exist that year"}

# Timeliness metadata that is not stored inside the files themselves.
# Source: each provider's documentation page (see ProjectPlan.md references).
SOURCE_PERIODS = {
    "usda": {"measure": "GROC20", "observation_year": 2020,
             "release": "Food Environment Atlas, July 2025 release"},
    "census": {"measure": "POPESTIMATE2020", "observation_year": 2020,
               "release": "Vintage 2024 county population estimates (July 1, 2020 estimate)"},
    "places": {"measure": "DIABETES_CrudePrev", "observation_year": 2022,
               "release": "PLACES 2024 release (model-based estimates from 2022 BRFSS)"},
}


# ---------------------------------------------------------------- loading

def load_usda():
    """Return the long-format USDA table and the release note from the zip README."""
    with zipfile.ZipFile(USDA_ZIP) as z:
        with z.open(USDA_MEMBER) as f:
            has_bom = f.read(3) == b"\xef\xbb\xbf"
        with z.open(USDA_MEMBER) as f:
            # utf-8-sig strips the byte-order mark at the start of the header.
            df = pd.read_csv(io.TextIOWrapper(f, encoding="utf-8-sig"), dtype=str, keep_default_na=False)
        readme = z.read(USDA_README).decode("utf-8", errors="replace")
    release = re.search(r"original release date of this file is ([^.\n]+)", readme)
    return df, (release.group(1).strip() if release else None), has_bom


def load_census():
    # Census Bureau CSVs may contain Latin-1 characters in place names.
    return pd.read_csv(CENSUS_CSV, dtype=str, encoding="latin-1", keep_default_na=False)


def load_places():
    return pd.read_csv(PLACES_CSV, dtype=str, keep_default_na=False)


# ---------------------------------------------------------------- helpers

def numeric(series):
    """Convert text to numbers; anything unparseable becomes NaN."""
    return pd.to_numeric(series.str.replace(",", "", regex=False).str.strip(), errors="coerce")


def describe(values):
    v = values.dropna()
    if v.empty:
        return {}
    return {"min": float(v.min()), "median": float(v.median()), "mean": round(float(v.mean()), 3),
            "max": float(v.max())}


def key_checks(keys):
    """Consistency checks shared by every source's FIPS key."""
    return {
        "rows": int(len(keys)),
        "invalid_fips_format": int((~keys.str.match(FIPS_PATTERN)).sum()),
        "duplicate_fips": int(keys.duplicated().sum()),
        "state_level_rows_ending_000": int(keys.str.endswith("000").sum()),
    }


# ---------------------------------------------------------------- per-source profiles

def profile_usda(df, release_note, has_bom):
    groc = df[df["Variable_Code"] == "GROC20"].copy()
    raw_values = groc["Value"].str.strip()
    groc["value"] = numeric(raw_values)
    groc16 = df[df["Variable_Code"] == "GROC16"].copy()
    groc16["value"] = numeric(groc16["Value"])

    sentinel_counts = {code: int((raw_values == code).sum()) for code in USDA_SENTINELS}
    text_missing = int(raw_values.isin(["", "N/A", "NA"]).sum())
    valid = groc[groc["value"] >= 0]
    suppressed = groc[raw_values == "-9999"]

    return {
        "file": f"{USDA_ZIP.relative_to(ROOT)}::{USDA_MEMBER}",
        "total_rows_long_format": int(len(df)),
        "distinct_variables": int(df["Variable_Code"].nunique()),
        "accuracy": {
            "groc20_valid_summary": describe(valid["value"]),
            "negative_values_other_than_sentinels": int(
                ((groc["value"] < 0) & ~raw_values.isin(USDA_SENTINELS)).sum()),
            "non_integer_counts": int((valid["value"] % 1 != 0).sum()),
            "true_zero_counts": int((groc["value"] == 0).sum()),
        },
        "completeness": {
            "groc20_rows": int(len(groc)),
            "sentinel_counts": {f"{k} ({v})": sentinel_counts[k] for k, v in USDA_SENTINELS.items()},
            "blank_or_NA_text": text_missing,
            "usable_groc20_values": int(len(valid)),
            "usable_share": round(len(valid) / len(groc), 4),
            "suppressed_by_state_top10": suppressed["State"].value_counts().head(10).to_dict(),
            "minus_8888_counties": groc.loc[raw_values == "-8888", ["FIPS", "State", "County"]]
                                      .to_dict("records"),
            # Suppression check: if counts of 1-2 stores vanish in 2020 but existed in 2016,
            # the -9999 counties are likely small-count counties, i.e. missing NOT at random.
            "groc20_counties_with_1_or_2_stores": int(groc["value"].between(1, 2).sum()),
            "groc16_counties_with_1_or_2_stores": int(groc16["value"].between(1, 2).sum()),
            "groc16_minus_9999": int((groc16["Value"].str.strip() == "-9999").sum()),
        },
        "timeliness": {**SOURCE_PERIODS["usda"], "release_note_in_zip": release_note},
        "consistency": {**key_checks(groc["FIPS"]),
                        "header_had_byte_order_mark": has_bom,
                        "value_column_stored_as_text_with_mixed_codes": True},
    }, groc


def profile_census(df):
    counties = df[df["SUMLEV"] == "050"].copy()
    states = df[df["SUMLEV"] == "040"].copy()
    counties["FIPS"] = counties["STATE"].str.zfill(2) + counties["COUNTY"].str.zfill(3)
    counties["pop"] = numeric(counties["POPESTIMATE2020"])
    states["pop"] = numeric(states["POPESTIMATE2020"])

    # Accuracy cross-check: county populations should add up to the state row.
    county_sums = counties.groupby("STATE")["pop"].sum()
    state_totals = states.set_index("STATE")["pop"]
    mismatched_states = [s for s in state_totals.index
                         if abs(county_sums.get(s, 0) - state_totals[s]) > 0]

    return {
        "file": str(CENSUS_CSV.relative_to(ROOT)),
        "total_rows": int(len(df)),
        "rows_by_SUMLEV": df["SUMLEV"].value_counts().to_dict(),
        "accuracy": {
            "pop2020_summary": describe(counties["pop"]),
            "pop_zero_or_negative": int((counties["pop"] <= 0).sum()),
            "states_where_county_sum_differs_from_state_total": mismatched_states,
        },
        "completeness": {
            "county_rows": int(len(counties)),
            "pop2020_missing_or_non_numeric": int(counties["pop"].isna().sum()),
        },
        "timeliness": SOURCE_PERIODS["census"],
        "consistency": {**key_checks(counties["FIPS"]),
                        "STATE_widths": sorted(counties["STATE"].str.len().unique().tolist()),
                        "COUNTY_widths": sorted(counties["COUNTY"].str.len().unique().tolist()),
                        "connecticut_codes": counties.loc[counties["STATE"] == "09", "FIPS"].tolist()},
    }, counties


def profile_places(df):
    df = df.copy()
    df["diab"] = numeric(df["DIABETES_CrudePrev"])

    # Accuracy cross-check: the point estimate should sit inside its own 95% CI.
    ci = df["DIABETES_Crude95CI"].str.extract(r"\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)").astype(float)
    outside_ci = int(((df["diab"] < ci[0]) | (df["diab"] > ci[1])).sum())

    return {
        "file": str(PLACES_CSV.relative_to(ROOT)),
        "total_rows": int(len(df)),
        "accuracy": {
            "diabetes_summary": describe(df["diab"]),
            "diabetes_outside_0_100": int(((df["diab"] < 0) | (df["diab"] > 100)).sum()),
            "estimate_outside_own_95ci": outside_ci,
            "unparseable_ci": int(ci[0].isna().sum()),
        },
        "completeness": {
            "diabetes_missing_or_non_numeric": int(df["diab"].isna().sum()),
        },
        "timeliness": SOURCE_PERIODS["places"],
        "consistency": {**key_checks(df["CountyFIPS"]),
                        "TotalPopulation_has_thousands_commas": int(
                            df["TotalPopulation"].str.contains(",", regex=False).sum()),
                        "connecticut_codes": sorted(
                            df.loc[df["CountyFIPS"].str.startswith("09"), "CountyFIPS"].tolist())},
    }, df


# ---------------------------------------------------------------- integration feasibility

def integration_feasibility(groc, counties, places):
    u, c, p = set(groc["FIPS"]), set(counties["FIPS"]), set(places["CountyFIPS"])
    names = dict(zip(groc["FIPS"], groc["State"] + " - " + groc["County"]))
    names.update(zip(counties["FIPS"], counties["STNAME"] + " - " + counties["CTYNAME"]))

    usable_usda = set(groc.loc[groc["value"] >= 0, "FIPS"])
    usable_places = set(places.loc[places["diab"].notna(), "CountyFIPS"])
    usable_census = set(counties.loc[counties["pop"] > 0, "FIPS"])

    def labelled(keys):
        return [f"{k} ({names.get(k, '?')})" for k in sorted(keys)]

    return {
        "key": "5-character county FIPS code stored as text",
        "source_key_counts": {"usda": len(u), "census": len(c), "places": len(p)},
        "pairwise_overlap": {"usda_census": len(u & c), "usda_places": len(u & p),
                             "census_places": len(c & p)},
        "in_all_three": len(u & c & p),
        "unmatched": {
            "usda_only": labelled(u - c - p),
            "census_and_places_not_usda": labelled((c & p) - u),
            "other": labelled((u | c | p) - (u & c & p) - (u - c - p) - ((c & p) - u)),
        },
        "sample_attrition": {
            "keys_in_all_three": len(u & c & p),
            "after_dropping_usda_sentinels": len(usable_usda & c & p),
            "with_all_three_measures_usable": len(usable_usda & usable_census & usable_places),
        },
    }


# ---------------------------------------------------------------- report writing

def to_markdown(results):
    lines = ["# Pre-integration data quality profile", "",
             "Generated by [`src/profile_sources.py`](../../src/profile_sources.py). "
             "Raw files are read only; nothing in `data/raw/` is changed.", ""]
    titles = {"usda": "USDA Food Environment Atlas (GROC20)",
              "census": "Census county population estimates (POPESTIMATE2020)",
              "places": "CDC PLACES county data (DIABETES_CrudePrev)"}
    for key, title in titles.items():
        section = results[key]
        lines += [f"## {title}", "", f"File: `{section['file']}`", ""]
        for dim in ("accuracy", "completeness", "timeliness", "consistency"):
            lines.append(f"**{dim.capitalize()}**")
            lines.append("")
            for name, value in section[dim].items():
                lines.append(f"- `{name}`: {json.dumps(value, ensure_ascii=False)}")
            lines.append("")
    feas = results["integration_feasibility"]
    lines += ["## Integration feasibility", "", f"Join key: {feas['key']}.", ""]
    for name, value in feas.items():
        if name != "key":
            lines.append(f"- `{name}`: {json.dumps(value, ensure_ascii=False)}")
    lines.append("")
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    usda_raw, release_note, has_bom = load_usda()
    usda_profile, groc = profile_usda(usda_raw, release_note, has_bom)
    census_profile, counties = profile_census(load_census())
    places_profile, places = profile_places(load_places())

    results = {
        "usda": usda_profile,
        "census": census_profile,
        "places": places_profile,
        "integration_feasibility": integration_feasibility(groc, counties, places),
    }

    (OUT / "pre_integration_profile.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    (OUT / "pre_integration_profile.md").write_text(to_markdown(results))
    att = results["integration_feasibility"]["sample_attrition"]
    print(f"Profile written to {OUT.relative_to(ROOT)}/ "
          f"(counties with all three measures usable: {att['with_all_three_measures_usable']})")


if __name__ == "__main__":
    main()
