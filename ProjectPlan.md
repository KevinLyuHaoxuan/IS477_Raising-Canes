# County Grocery Store Availability and Diabetes Prevalence

## Overview

This project asks whether U.S. counties with fewer grocery stores per 10,000 residents tend to have higher estimated adult diabetes prevalence. We will combine county data from the USDA Economic Research Service, the Centers for Disease Control and Prevention (CDC), and the U.S. Census Bureau, linking records by county FIPS code. We will use the 2020 grocery-store count and population estimate to calculate store availability, then compare it with the CDC's modeled diabetes estimate for 2022.

Our goal is not to claim that grocery stores cause or prevent diabetes. We want to build a small, reproducible data-curation workflow: acquire three public datasets, assess and clean them, integrate them, and present a simple analysis with a visualization. We will keep the question narrow so we can focus on careful data handling and explain each step clearly.

## Team

Each member will lead one area throughout the project and contribute to the related parts of this plan and later reports. Everyone will review the work, and each member will commit their own contributions to the shared repository.

| Member | Primary responsibility |
|---|---| 
| Haoxuan Lyu | Integration and analysis: join the data, calculate grocery stores per 10,000 residents, and lead analysis and visualization. |
| Jihyun Seo (Ji) | Data quality and cleaning: profile the data, assess quality, document issues, and implement cleaning. |
| Ayan Bhakta | Workflow and reproducibility: organize scripts and the run-all workflow, dependencies, relative paths, metadata, and reproduction instructions. |
| Rishi Vemulapalli | Data sources and acquisition: obtain files and document provenance, use terms, and download/checksum records. |

These roles identify primary owners, not separate silos. Members will review decisions that affect other stages and help test the complete workflow.

## Research Question

**Across U.S. counties with usable data, is a lower number of grocery stores per 10,000 residents associated with a higher CDC-estimated adult diabetes prevalence?** We will calculate the grocery-store rate as `GROC20 / POPESTIMATE2020 * 10,000`, then use descriptive statistics, a scatterplot, and a simple correlation measure to describe the relationship. This is an observational, county-level study; we will report association, not causation or individual-level effects.

## Datasets

We will use three complementary, non-Kaggle datasets, each with far more than 100 county records. Each adds information needed for the question.

1. **USDA Food Environment Atlas, archived 2020 data.** We will use the county-level 2020 grocery-store count (`GROC20`) and county FIPS/GEOID. USDA defines grocery stores as supermarkets and grocery stores in NAICS 445110. This provides the store-availability measure.
2. **CDC PLACES County Data, 2024 release, GIS-friendly format.** We will use `countyfips` and `DIABETES_CrudePrev`, the model-based estimate of crude adult diabetes prevalence for 2022. This provides the health outcome. The release has 3,144 county-level records and uses BRFSS, Census population estimates, and ACS data to produce its estimates.
3. **U.S. Census Bureau Population Estimates Program, county totals, 2020–2024.** We will use `SUMLEV`, `STATE`, `COUNTY`, and `POPESTIMATE2020`, keeping county-level rows. We will zero-pad and combine the state and county FIPS components to create the five-character join key. This provides the population denominator, allowing store availability to be compared across counties of different sizes.

We will store FIPS codes as text to preserve leading zeros and join using exact matches. A preliminary check found about 2,226 counties with usable data after excluding missing USDA store counts; our scripts will recalculate this number and document the final match rate. County-equivalent definitions can change between data vintages, so we will investigate and report unmatched codes rather than force uncertain name-based matches.

## Lifecycle, Organization, and Methods

We will map the work to the data-lifecycle framework covered in Module 1: plan, acquire, assess and process, preserve, analyze, and share. Original files will go in `data/raw/`, cleaned and integrated tables in `data/processed/`, code in `src/`, and figures and summary outputs in `outputs/`. We will use CSV for tables and JSON for machine-readable metadata. Raw files will remain unchanged after download.

Before integration, we will assess all four required quality dimensions. **Accuracy:** check values against source definitions and plausible ranges, including positive population and diabetes prevalence between 0 and 100. **Completeness:** count missing values, missing county records, duplicate keys, and USDA sentinel codes. **Timeliness:** record publication and observation years, including the 2020 USDA/Census values and 2022 CDC estimate. **Consistency:** check data types, units, five-character FIPS formatting, and uniqueness of county keys. We will save the checks and findings in a quality report.

Cleaning will be limited to reproducible, documented steps. We will convert USDA `N/A`, `-9999`, and `-8888` values to missing, preserve FIPS as five-character text, filter the Census file to county-level rows, and investigate duplicate keys. We will not impute missing grocery counts or diabetes estimates. Rows missing required measures or having an invalid population denominator will be excluded from analysis, with reasons and counts recorded.

After integration, we will reassess accuracy, completeness, timeliness, and consistency. We will check join cardinality and match rate, duplicate keys, missingness, plausible ranges, and the derived store-rate calculation. These results will show whether the join worked and where coverage is limited. We will then produce descriptive statistics and a scatterplot. The analysis will remain simple; the main emphasis is a clear curation chain.

## Ethics, Terms, and Constraints

These sources contain county-level aggregate statistics, not personal records, so we do not expect to handle personally identifiable information. CDC metadata identifies its dataset as public domain. Before redistributing source files, we will verify reuse and attribution terms for all sources, cite them, preserve their documentation, and record data and software licenses in the repository. We plan to include input files in GitHub if they are redistributable and below the course's 50 MB limit; otherwise, we will follow the course's Box and download-code instructions.

The CDC diabetes values are modeled estimates, not direct counts. Grocery-store counts do not represent store size, prices, quality, or where residents shop. The store and population measures are from 2020 while the CDC estimate is for 2022, so the periods are not identical. County-level results cannot establish individual behavior or causation. FIPS changes may also leave some counties unmatched. We will report these limits and avoid overstating conclusions.

## Workflow and Reproducibility

We will create separate scripts for acquisition and SHA-256 checksums, source profiling, cleaning, integration and post-integration checks, and analysis/visualization. A `run_all.py` script will call each stage in order. The repository will use relative paths, declare packages in `requirements.txt`, and document the run order. We will include a data dictionary and machine-readable metadata using DCAT, DataCite, or Schema.org. Before the final release, Ayan will coordinate a full run from a fresh clone, and all members will test it.

## Timeline

| Dates | Tasks and deliverables | Lead(s) |
|---|---|---|
| Oct. 12, 2026 | Finalize `ProjectPlan.md`, create the project-plan release, and submit its URL to Canvas. | All; Haoxuan coordinates integration of the plan |
| Oct. 13–20 | Acquire data; document sources, terms, versions, and checksums. | Rishi; Ayan supports automation |
| Oct. 21–30 | Complete source quality profiles and cleaning. | Ji; Rishi reviews source definitions |
| Oct. 31–Nov. 7 | Integrate datasets, assess the merged table, and produce an initial analysis and plot. | Haoxuan; Ji reviews quality results |
| Nov. 8–18 | Connect scripts with the orchestrator; finish and test the interim report. | Ayan coordinates; all contribute |
| Nov. 19 | Release and submit the interim status report. | All |
| Nov. 20–Dec. 2 | Refine the pipeline and complete analysis, visualization, metadata, codebook, and README report. | All, by role |
| Dec. 3–6 | Test the full workflow from a fresh clone and complete final review. | Ayan coordinates; all test |
| Dec. 7 | Create the final-project release and submit its URL to Canvas. | All |

## Gaps

We still need to confirm the exact fields in the selected USDA archive, verify current reuse terms, and quantify unmatched county FIPS codes. We will also confirm the repository layout and agree on a final peer-review schedule. These open items will be checked during acquisition and do not change the proposed question or linkage strategy.

## References

- USDA Economic Research Service. [Food Environment Atlas: Data Access and Documentation Downloads](https://www.ers.usda.gov/data-products/food-environment-atlas/data-access-and-documentation-downloads) and [Documentation](https://www.ers.usda.gov/data-products/food-environment-atlas/documentation).
- Centers for Disease Control and Prevention. [PLACES: County Data (GIS-Friendly Format), 2024 release](https://data.cdc.gov/500-Cities-Places/PLACES-County-Data-GIS-Friendly-Format-2024-releas/d3i6-k6z5).
- U.S. Census Bureau. [County Population Estimates, 2020–2024 CSV](https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv) and [file layout](https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2020-2024/CO-EST2024-ALLDATA.pdf).
