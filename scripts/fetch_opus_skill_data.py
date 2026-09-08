"""
Job Market Intelligence - Stage 3a: Fetch real skill vocabulary from OPUS
--------------------------------------------------------------------------
Pulls the REAL distinct candidate skills from the OPUS pipeline's
int_skills_normalized model (a genuinely separate GCP project) and saves
them as a dbt seed -- this is the actual cross-project integration this
whole project is built around, not a simulated join.

Requires the OPUS project's service account key. Adjust OPUS_KEY_PATH
below if your opus-data-pipeline project folder is somewhere other than
a sibling directory to this one.

Usage:
    python scripts/fetch_opus_skill_data.py
"""

import os
import csv

from google.cloud import bigquery
from google.oauth2 import service_account

OPUS_PROJECT_ID = "opus-data-pipeline"
OPUS_KEY_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data-pipeline", "gcp-service-account.json"
)

SEEDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "seeds")


def main():
    if not os.path.exists(OPUS_KEY_PATH):
        raise RuntimeError(
            f"OPUS service account key not found at {os.path.normpath(OPUS_KEY_PATH)}. "
            f"Update OPUS_KEY_PATH in this script to point at your OPUS project's "
            f"gcp-service-account.json."
        )

    credentials = service_account.Credentials.from_service_account_file(OPUS_KEY_PATH)
    client = bigquery.Client(project=OPUS_PROJECT_ID, credentials=credentials)

    # Real candidate skills only (source_field='user_settings'), not the
    # empty platform_jobs.skills we confirmed in the OPUS project's Step 2.
    query = """
        SELECT
            skill_normalized,
            COUNT(DISTINCT entity_id) as candidate_count
        FROM `opus-data-pipeline.dbt_dev.int_skills_normalized`
        WHERE source_field = 'user_settings'
        GROUP BY skill_normalized
        ORDER BY candidate_count DESC
    """

    print("Querying OPUS project for real candidate skill data...")
    rows = list(client.query(query).result())

    os.makedirs(SEEDS_DIR, exist_ok=True)
    out_path = os.path.join(SEEDS_DIR, "opus_candidate_skills.csv")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["skill_normalized", "candidate_count"])
        for row in rows:
            writer.writerow([row.skill_normalized, row.candidate_count])

    print(f"Fetched {len(rows)} distinct real candidate skills.")
    print(f"Written to {os.path.normpath(out_path)}")


if __name__ == "__main__":
    main()