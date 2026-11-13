# Interim Status Report — County Grocery Store Availability and Diabetes Prevalence

**IS 477 · Team Raising Canes · November 13, 2026**

## Project status

Our project asks whether U.S. counties with fewer grocery stores per 10,000 residents tend to have higher estimated adult diabetes prevalence. The [current project plan](ProjectPlan.md) specifies three complementary sources and the county Federal Information Processing Standards (FIPS) code as the linkage key. USDA supplies the store count, Census supplies the population denominator, and CDC supplies the health measure. This is a county-level observational comparison, so the final interpretation will be limited to the association we observe across counties with usable data.

The [project-plan release](https://github.com/KevinLyuHaoxuan/IS477_Raising-Canes/releases/tag/project-plan) is published. The [repository README](README.md) identifies the team, and the current plan defines the research question, source fields, roles, and proposed quality checks. As of this update, the shared Git history supports reporting progress on planning and source selection. Acquisition, cleaning, integration, and analysis remain pending verification against committed artifacts. The plan mentions a preliminary estimate of about 2,226 usable counties after excluding missing USDA counts. We will recalculate that figure from the pinned inputs and publish a record of exclusions and join losses before citing a final sample size.

## Progress by task

**Source selection and acquisition — Rishi Vemulapalli, with automation support from Ayan Bhakta.** The plan identifies USDA Food Environment Atlas `GROC20`, CDC PLACES 2024 GIS-friendly county data `DIABETES_CrudePrev`, and Census Population Estimates Program county totals `POPESTIMATE2020`. The next deliverable is a source manifest containing the exact file or archive member for each input, the source URL, release vintage, retrieval date, reuse terms, and SHA-256 checksum. The acquisition script should place unchanged inputs under `data/raw/` and verify pinned hashes on subsequent runs. USDA’s exact release vintage and redistribution terms still need confirmation. Raw files eligible for GitHub distribution can be committed there. Files subject to the course’s Box requirement will need a grader-accessible link and tested download code.

**Source profiling and cleaning — Jihyun Seo, with source-definition review from Rishi.** The plan defines checks across accuracy, completeness, timeliness, and consistency. Accuracy checks include prevalence between zero and 100 and a positive population. Completeness checks include missing measures, sentinel values, and absent county records. Timeliness checks will record both observation year and publication vintage. Consistency checks will confirm units, five-character FIPS formatting, and uniqueness of the county key. The next deliverable is a reproducible profile with counts for each source, followed by a cleaning script that addresses the observed issues. The script should retain genuine zero store counts, convert the documented USDA sentinel values to missing, and filter the Census input to county-level records before building the key from its state and county fields.

**Integration, post-integration quality, and initial analysis — Haoxuan Lyu, with quality review from Jihyun.** The planned join uses exact five-character county identifiers. The next deliverable is a join audit with source counts, unique keys, overlaps, unmatched keys by source, and counts of rows removed from the analysis table. The integration script should check one-to-one join cardinality and flag duplicates for review. The post-integration assessment should verify the rate calculation, check missingness and coverage after joining, carry the observation years forward, and confirm a consistent county-level schema. For the first analysis, the team will report descriptive statistics, a scatterplot, and a correlation for grocery stores per 10,000 residents versus modeled adult diabetes prevalence.

**Workflow, documentation, and reproducibility — Ayan, with testing by the team.** The plan specifies separate scripts for acquisition, profiling, cleaning, integration and validation, and analysis. The next deliverable is the stage interface and a `run_all.py` entry point that calls the scripts in order and stops when a stage fails. Each stage should read and write documented repository-relative paths so a teammate can rerun it independently. The final documentation will include dependency versions, reproduction commands, a data dictionary, machine-readable metadata, source citations, and data and software licensing information. The final test will use a fresh clone and compare the resulting outputs against the committed analysis.

## Changes to the plan and challenges

The [documented plan revision](https://github.com/KevinLyuHaoxuan/IS477_Raising-Canes/commit/8e8e0d0833dfdd9314582d173200137f8ce04601) updates the USDA dataset and expands the constraints. We are carrying that revision forward and moving the original October and early November targets to the proposed dates below because the corresponding deliverables have yet to be verified in GitHub. Instructor feedback for Milestone 2 has yet to be confirmed for this report. Once available, the team should tie each resulting change to the relevant plan section or artifact.

- **Changing county boundaries.** The Census vintage uses Connecticut planning regions, which may differ from the geographic units in the other sources. The join audit will list those keys and count their exclusions. Any geographic crosswalk would require a documented mapping that preserves the intended unit of analysis.
- **Missing and invalid values.** A missing store count changes which counties enter the analysis. The cleaning step will preserve valid zeroes, record each exclusion reason, and summarize whether exclusions are geographically concentrated. A missing or nonpositive population makes the store rate undefined.
- **Different measurement years.** Store availability and population use 2020 values, while the CDC estimate describes 2022. The analysis will label these years in the table, figure, and narrative. It will also describe the CDC measure as modeled and explain that a store count measures availability only at the county level.
- **Reproducible inputs.** Publisher downloads may change over time. The source manifest will identify the exact snapshot, hash, and retrieval method. A fresh-clone test will check whether all inputs can be acquired and processed using the documented commands.

## Updated timeline

The dates below are proposed working targets. The milestone release should follow the deadline shown in Canvas.

| Task | Status | Proposed target and lead |
|---|---|---|
| Project plan and release | Published | Oct. 12, all members |
| Confirm inputs, terms, and checksums | Sources selected, artifacts pending verification | Nov. 15, Rishi and Ayan |
| Profile sources and implement cleaning | Checks specified, results pending verification | Nov. 18, Jihyun and Rishi |
| Join, validate, and produce initial analysis | Linkage designed, outputs pending verification | Nov. 22, Haoxuan and Jihyun |
| Connect workflow stages and document dependencies | Structure specified, execution pending verification | Nov. 24, Ayan |
| Update report, commit work, and publish interim release | Report drafted, individual commits and release pending | By Canvas deadline, all members |
| Finish analysis, metadata, codebook, licensing, and README | Planned | Dec. 2, all members by role |
| Test from a fresh clone and complete final review | Planned | Dec. 3–6, Ayan coordinates and all members test |
| Publish final release and submit its URL | Planned | Dec. 7, all members |

## Individual contribution summaries

Each team member will add a short summary of their own completed work to this section and commit it from their GitHub account. The [team section of the project plan](ProjectPlan.md#team) records assigned responsibilities. Individual summaries will identify the work completed for this milestone and link to the corresponding files or commits.
