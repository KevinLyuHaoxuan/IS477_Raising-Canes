# Interim Status Report

**Raising Canes · IS 477 · November 13, 2026**

## What we’re studying

Do U.S. counties with fewer grocery stores per 10,000 residents tend to have higher adult diabetes prevalence? To answer that, we need three pieces of information for each county: a grocery store count from the USDA, a population estimate from the Census Bureau, and a diabetes prevalence estimate from the CDC. Dividing store counts by population lets us compare counties of different sizes. For example, ten grocery stores mean something different in a county of 20,000 people than in a county of 200,000.

The [project plan](ProjectPlan.md) and [October 12 release](https://github.com/KevinLyuHaoxuan/IS477_Raising-Canes/releases/tag/project-plan) are on GitHub. The plan records a preliminary count of about 2,226 usable counties after excluding missing USDA store counts. That is a starting point for checking our results. The final count will come from the scripted join and will include a breakdown of counties that failed to match or were missing one of the measures. The shared repository currently contains the plan and report documents. Data acquisition, cleaning, integration, and analysis are not yet complete.

## Where each part of the project stands

### Acquisition and source documentation

Rishi is leading acquisition, with Ayan helping automate it. We’ve identified the exact fields for the analysis. The [USDA Food Environment Atlas](https://www.ers.usda.gov/data-products/food-environment-atlas/data-access-and-documentation-downloads) supplies the 2020 grocery store count, `GROC20`. The [Census county population file](https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv) supplies `POPESTIMATE2020`. The [2024 CDC PLACES county release](https://data.cdc.gov/500-Cities-Places/PLACES-County-Data-GIS-Friendly-Format-2024-releas/d3i6-k6z5) supplies `DIABETES_CrudePrev`, which estimates prevalence in 2022.

The open item from the project plan was to record the exact release of each source, so that our results can be traced back to a specific version of the data. We have now confirmed each release. The USDA file is the July 2025 release of the Food Environment Atlas, as stated in `ReadMeFile2025.txt` inside the zip. The Census file is the Vintage 2024 county estimates, and the CDC file is the 2024 PLACES release. To record each version, Rishi wrote [`src/checksums.py`](src/checksums.py), which computes a SHA-256 checksum for each raw file and saves the results to [`outputs/provenance/checksums.csv`](outputs/provenance/checksums.csv). If a source is downloaded again and its checksum does not match, we will know the data has changed. We also checked the reuse terms and file sizes. The [CDC dataset page](https://data.cdc.gov/500-Cities-Places/PLACES-County-Data-GIS-Friendly-Format-2024-releas/d3i6-k6z5) lists the license as Public Domain and states that the data are publicly available without restrictions. The [Census Bureau](https://www.census.gov/about/policies/open-gov.html) states that it publishes its data as open data that is freely available for use and re-use by the public. The [USDA documentation](https://www.ers.usda.gov/data-products/food-environment-atlas/documentation) does not state a license, but it provides a recommended citation, which we will use. Each file is under the 50 MB limit, with the largest at about 6.5 MB, so the raw files can remain in [`data/raw/`](data/raw/) and do not need to be stored on Box. The raw files will stay as received, and cleaned versions will be written separately.

### Quality assessment and cleaning

Jihyun is leading this part, with Rishi checking the source definitions. Before joining anything, we’ll profile the three inputs and save the counts. For accuracy, we’ll check for prevalence outside zero to 100 and population values at or below zero. For completeness, we’ll count missing values and look for county records missing from each source. For timeliness, we’ll record the year each measure describes alongside its publication year. For consistency, we’ll check that county codes follow the same format, that each source has one row per county after filtering, and that each measure uses the expected units.

The biggest cleaning decision is how to handle missing store counts. We’ll check the source documentation for `N/A`, `-9999`, and `-8888` and convert documented missing-value codes before calculating rates. A genuine zero remains in the analysis because zero stores is a meaningful count. We’ll filter the Census file to county rows and build the join key by combining the two-digit state code and three-digit county code. We’ll preserve leading zeros across all three files and log which rows fail the checks, so a reader can trace why each row was excluded.

### Joining the sources and checking the result

Haoxuan is leading integration and analysis, with Jihyun reviewing the quality checks. We’ll join on the five-character county FIPS code and check for duplicate keys before merging. Connecticut is the first place we’ll investigate if the keys don’t line up. The Census vintage uses planning regions, and the other files may use older county boundaries. Joining those rows by a similar name could attach a store count to the wrong population. We’ll list the unmatched identifiers and report how many counties the mismatch affects.

After the join, we’ll check the four quality dimensions again. We’ll recalculate the store rate from the source fields to check accuracy, compare the final row count with the source and overlap counts to check completeness, verify that the year labels stayed with the measures, and check that the merged table still has one row per FIPS code. Then we’ll make a scatterplot and calculate the correlation. We’ll report how many counties appear in the figure and examine whether exclusions are concentrated in particular states. The 2020 store measure and the 2022 health measure are two years apart, and a county-level comparison can describe an association across counties.

One result we’ll look at closely is how the sample changes from one step to the next. We’ll start with the county counts for each source, then show how many counties share a key and how many still have all three usable measures. That breakdown will help explain any difference from the preliminary 2,226 figure. If missing grocery counts account for most of the drop, we’ll check which states account for those missing records. If the drop happens during the join, we’ll inspect the unmatched codes and compare the county definitions in the source documentation.

### Putting the workflow together

Ayan is responsible for connecting the stages and documenting how to run them. The workflow will use separate scripts for acquisition, profiling, cleaning, joining and validating, and analysis. A `run_all.py` script will call them in that order and stop if a stage fails. We’ll agree on input and output filenames before wiring the scripts together, so a teammate can rerun the cleaning or join step on its own. The final README will include the installation and run commands, pinned dependencies, and links to the outputs. We’ll also add a codebook and machine-readable metadata, then test the instructions from a fresh clone.

## Changes since the project plan

The [revision on GitHub](https://github.com/KevinLyuHaoxuan/IS477_Raising-Canes/commit/8e8e0d0833dfdd9314582d173200137f8ce04601) updates the USDA source and expands the constraints section. The research question and county FIPS linkage are still the basis of the project. The original schedule called for acquisition by October 20, cleaning by October 30, and the first join and plot by November 7. The shared repository still needs the files that would demonstrate those steps, so the dates below are revised targets for getting the work into GitHub. The Milestone 2 submission received 20 out of 20. The instructor's written comment praised the detail of the plan and did not identify a specific revision. The USDA and constraints changes linked above were made on October 12, before that feedback was posted on November 2, so they are not presented as changes made in response to it.

## Revised schedule

The following dates are proposed targets for the remaining work, not a record of completed tasks. Canvas lists the interim report deadline as November 16 at 3:30 p.m. The report and available work must be pushed and released by that deadline, even if the later technical stages remain unfinished.

- **November 15:** Rishi will confirm the source snapshots and reuse terms. Ayan will help document retrieval and checksum verification.
- **November 16 by 3:30 p.m.:** All members will add their own contribution summaries, commit the work available for review, and create the `status-report` release. The release URL will be submitted through Canvas.
- **November 18:** Jihyun will aim to commit the source profiles and cleaning steps. Rishi will review how the scripts interpret source fields and missing-value codes.
- **November 22:** Haoxuan will aim to commit the merged county data, join audit, and initial scatterplot. Jihyun will review the exclusions and merged-table checks.
- **November 24:** Ayan will aim to connect the scripts, document dependencies, and run the workflow from acquisition through the first plot.
- **December 2:** The team will finish the analysis, codebook, metadata, licensing, and final README.
- **December 3–7:** The team will test the workflow from a fresh clone December 3–6 and target December 7 for the final release.

For the interim milestone, each team member will add their own contribution summary to this report and commit it under their GitHub account. The team will push the work available by the Canvas deadline and use that snapshot for the `status-report` release.

## Individual contribution summary

### Haoxuan Lyu

I contributed the initial [project plan](https://github.com/KevinLyuHaoxuan/IS477_Raising-Canes/commit/77a7a314d238262246c875247079390365ccf4a6), which defined the county-level research question, the three sources, and the proposed FIPS-based integration and analysis. This contribution was made for the earlier project-plan milestone. For the current milestone, my assigned responsibility is to develop the integration and analysis once the source and cleaning outputs are available. The join, its quality checks, and the initial figure are not yet complete.

### Jihyun Seo

I downloaded the three source files and added them to [`data/raw/`](data/raw/), and wrote [`src/profile_sources.py`](src/profile_sources.py), which profiles each source before integration across accuracy, completeness, timeliness, and consistency and checks join feasibility on county FIPS. Results are in [`outputs/quality/pre_integration_profile.md`](outputs/quality/pre_integration_profile.md). The profile reproduces the 2,226 usable counties from our plan and explains the drop: 909 USDA counties are coded `-9999`, one Alaska county is `-8888`, and Connecticut does not match because Census and PLACES use planning regions while USDA uses the old counties. The profile also shows that no county has 1 or 2 grocery stores in 2020 (727 did in 2016), which suggests the suppressed counties are mostly low-store counties. This would bias our sample, so we will address it in the cleaning step and the report. Next, I will write the cleaning script by November 18.

### Rishi Vemulapalli

In the project plan, I [corrected the USDA dataset and wrote the constraints section](https://github.com/KevinLyuHaoxuan/IS477_Raising-Canes/commit/8e8e0d0833dfdd9314582d173200137f8ce04601). For this milestone, my responsibility was to document where each raw file came from, so that our analysis can be traced back to a specific version of each source. First, I confirmed the release of each file. The USDA file is the July 2025 release of the Food Environment Atlas, the Census file is the Vintage 2024 county estimates, and the CDC file is the 2024 PLACES release. Next, I wrote [`src/checksums.py`](src/checksums.py), which computes a SHA-256 checksum for each file in `data/raw/` and saves the results to [`outputs/provenance/checksums.csv`](outputs/provenance/checksums.csv). If a source is downloaded again and its checksum does not match, we will know the data has changed. I also checked the reuse terms and file sizes. All three sources are public government data and each file is under the 50 MB limit, so the raw files can remain in the repository. By November 18, I will review how the cleaning script interprets the sources and the USDA missing-value codes.
