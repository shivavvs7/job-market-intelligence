# Job Market Intelligence — Data Dictionary & Findings

Source: `arshkon/linkedin-job-postings` (Kaggle, license: CC-BY-SA-4.0 —
attribution required in any published analysis).

## Real counts (confirmed via profiling, not assumed)

| File | Rows | Notes |
|---|---|---|
| `postings.csv` | 123,849 | Main fact table |
| `companies/companies.csv` | 24,473 | Company dimension |
| `jobs/job_skills.csv` | 213,768 | Job-to-skill mapping (many-to-many) |
| `jobs/salaries.csv` | 40,785 | Dedicated salary table, separate from postings.csv's own salary fields |
| `mappings/skills.csv` | 35 | Skill abbreviation → name lookup |
| `mappings/industries.csv` | 422 | Industry ID → name lookup |

## Confirmed data quality findings

### 1. Salary data: use `salaries.csv`, not `postings.csv`'s own salary columns
`postings.csv` has its own `max_salary`/`min_salary`/`med_salary`/`normalized_salary`
columns, but they are 71–95% null. The dedicated `salaries.csv` table (joined
via `job_id`) has far better coverage — only 16.8% null on `max_salary`/`min_salary`.
**Decision: join to `salaries.csv` as the primary salary source; treat
`postings.csv`'s own salary fields as a fallback only.**

This is the same lesson as OPUS's `platform_jobs.skills` finding — verify a
field's actual usability before building on it, rather than trusting that a
column exists means it's populated.

### 2. `remote_allowed` is a presence flag, not a true boolean
Confirmed via direct value check: the column only ever contains `1.0` or
`NaN` — **never `0.0`**. A null does not necessarily mean "not remote"; it
likely means the poster simply didn't set the field. Any downstream logic
must not treat `NaN` as "confirmed non-remote" without acknowledging this
ambiguity.

### 3. `formatted_experience_level` — 23.7% null
Moderate but real gap. Worth deciding early whether to drop these rows from
experience-based analysis or bucket them as "Not specified" rather than
silently excluding them.

## Relational structure (for dimensional modeling in Stage 2)

- `postings.csv.job_id` → joins to `jobs/job_skills.csv`, `jobs/salaries.csv`,
  `jobs/benefits.csv`, `jobs/job_industries.csv`
- `postings.csv.company_id` → joins to `companies/companies.csv`,
  `companies/company_industries.csv`, `companies/company_specialities.csv`,
  `companies/employee_counts.csv`
- `jobs/job_skills.csv.skill_abr` → joins to `mappings/skills.csv` for the
  human-readable skill name (only 35 distinct skill categories — broad
  categories, not granular skills like OPUS's free-text skills)
- `jobs/job_industries.csv.industry_id` → joins to `mappings/industries.csv`

## Note on `mappings/skills.csv` scope
Only 35 rows — this is a small set of broad skill *categories* (e.g.
"Information Technology", "Sales"), not granular individual skills like
"Python" or "Docker". This is a different granularity than OPUS's
`int_skills_normalized` table. Cross-referencing OPUS candidate skills
against this dataset's skill categories will require a mapping step, not a
direct join — worth deciding the approach before building the skill-gap
model in Stage 3.

### 4. No granular skill data exists anywhere in this dataset — confirmed
Checked all three candidate sources for skill-level detail (e.g. "Python",
"Docker"), and none have it:
- `job_skills.csv` / `skills.csv`: only 35 broad functional categories (IT,
  Engineering, Sales, etc.) — confirmed by printing the full skills.csv.
- `postings.csv.skills_desc`: 98.0% null — effectively a dead field, same
  pattern as OPUS's empty `applications.attributes`.

**Decision: extract granular skills from `postings.csv.description`
(confirmed ~0% null, reliably populated) using keyword matching against
the known skill vocabulary already established in the OPUS project's
`int_skills_normalized` table.** This is a legitimate, real-world technique
for bootstrapping skill tagging from unstructured text, and it directly
enables the planned cross-source skill-gap analysis in Stage 3.
