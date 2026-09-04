# Kaggle LinkedIn Job Postings - Discovery Report

Source: `arshkon/linkedin-job-postings` (Kaggle, CC-BY-SA-4.0)


---

## `companies\companies.csv`

- File size: 22.1 MB
- Row count: 24,473

| Column | Dtype | Null % |
|---|---|---|
| `company_id` | int64 | 0.0% |
| `name` | str | 0.0% |
| `description` | str | 1.2% |
| `company_size` | float64 | 11.3% |
| `state` | str | 0.1% |
| `country` | str | 0.0% |
| `city` | str | 0.0% |
| `zip_code` | str | 0.1% |
| `address` | str | 0.1% |
| `url` | str | 0.0% |

---

## `companies\company_industries.csv`

- File size: 0.7 MB
- Row count: 24,375

| Column | Dtype | Null % |
|---|---|---|
| `company_id` | int64 | 0.0% |
| `industry` | str | 0.0% |

---

## `companies\company_specialities.csv`

- File size: 4.2 MB
- Row count: 169,387

| Column | Dtype | Null % |
|---|---|---|
| `company_id` | int64 | 0.0% |
| `speciality` | str | 0.0% |

---

## `companies\employee_counts.csv`

- File size: 1.0 MB
- Row count: 35,787

| Column | Dtype | Null % |
|---|---|---|
| `company_id` | int64 | 0.0% |
| `employee_count` | int64 | 0.0% |
| `follower_count` | int64 | 0.0% |
| `time_recorded` | int64 | 0.0% |

---

## `jobs\benefits.csv`

- File size: 1.8 MB
- Row count: 67,943

| Column | Dtype | Null % |
|---|---|---|
| `job_id` | int64 | 0.0% |
| `inferred` | int64 | 0.0% |
| `type` | str | 0.0% |

---

## `jobs\job_industries.csv`

- File size: 2.4 MB
- Row count: 164,808

| Column | Dtype | Null % |
|---|---|---|
| `job_id` | int64 | 0.0% |
| `industry_id` | int64 | 0.0% |

---

## `jobs\job_skills.csv`

- File size: 3.3 MB
- Row count: 213,768

| Column | Dtype | Null % |
|---|---|---|
| `job_id` | int64 | 0.0% |
| `skill_abr` | str | 0.0% |

---

## `jobs\salaries.csv`

- File size: 2.1 MB
- Row count: 40,785

| Column | Dtype | Null % |
|---|---|---|
| `salary_id` | int64 | 0.0% |
| `job_id` | int64 | 0.0% |
| `max_salary` | float64 | 16.8% |
| `med_salary` | float64 | 83.2% |
| `min_salary` | float64 | 16.8% |
| `pay_period` | str | 0.0% |
| `currency` | str | 0.0% |
| `compensation_type` | str | 0.0% |

---

## `mappings\industries.csv`

- File size: 0.0 MB
- Row count: 422

| Column | Dtype | Null % |
|---|---|---|
| `industry_id` | int64 | 0.0% |
| `industry_name` | str | 8.1% |

---

## `mappings\skills.csv`

- File size: 0.0 MB
- Row count: 35

| Column | Dtype | Null % |
|---|---|---|
| `skill_abr` | str | 0.0% |
| `skill_name` | str | 0.0% |

---

## `postings.csv`

- File size: 492.9 MB
- Row count: 123,849

| Column | Dtype | Null % |
|---|---|---|
| `job_id` | int64 | 0.0% |
| `company_name` | str | 1.4% |
| `title` | str | 0.0% |
| `description` | str | 0.0% |
| `max_salary` | float64 | 75.9% |
| `pay_period` | str | 70.9% |
| `location` | str | 0.0% |
| `company_id` | float64 | 1.4% |
| `views` | float64 | 1.4% |
| `med_salary` | float64 | 94.9% |
| `min_salary` | float64 | 75.9% |
| `formatted_work_type` | str | 0.0% |
| `applies` | float64 | 81.2% |
| `original_listed_time` | float64 | 0.0% |
| `remote_allowed` | float64 | 87.7% |
| `job_posting_url` | str | 0.0% |
| `application_url` | str | 29.6% |
| `application_type` | str | 0.0% |
| `expiry` | float64 | 0.0% |
| `closed_time` | float64 | 99.1% |
| `formatted_experience_level` | str | 23.7% |
| `skills_desc` | str | 98.0% |
| `listed_time` | float64 | 0.0% |
| `posting_domain` | str | 32.3% |
| `sponsored` | int64 | 0.0% |
| `work_type` | str | 0.0% |
| `currency` | str | 70.9% |
| `compensation_type` | str | 70.9% |
| `normalized_salary` | float64 | 70.9% |
| `zip_code` | float64 | 16.9% |
| `fips` | float64 | 22.1% |