"""
Job Market Intelligence - Stage 1: Ingest Kaggle CSVs -> GCS -> BigQuery
--------------------------------------------------------------------------
Uploads every CSV under data/raw/ to GCS, then loads each into BigQuery as
a raw table (autodetected schema, since these are already structured CSVs
-- unlike the OPUS project's Mongo JSON, there's no ambiguity to defer here).

Usage:
    python scripts/ingest_kaggle_to_gcs_bigquery.py
"""

import os

from dotenv import load_dotenv
from google.cloud import storage
from google.cloud import bigquery

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
DATASET_ID = "raw_market"

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH


def find_csv_files(root):
    csv_files = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(".csv"):
                full_path = os.path.join(dirpath, fname)
                # Table name = filename without extension (e.g. "postings", "job_skills")
                table_name = os.path.splitext(fname)[0]
                csv_files.append((table_name, full_path))
    return sorted(csv_files)


def ensure_bucket(storage_client):
    bucket = storage_client.bucket(BUCKET_NAME)
    if not bucket.exists():
        print(f"Creating bucket: {BUCKET_NAME}")
        storage_client.create_bucket(BUCKET_NAME, location="US")
    else:
        print(f"Using existing bucket: {BUCKET_NAME}")
    return bucket


def ensure_dataset(bq_client):
    dataset_ref = f"{GCP_PROJECT_ID}.{DATASET_ID}"
    try:
        bq_client.get_dataset(dataset_ref)
        print(f"Using existing dataset: {dataset_ref}")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        bq_client.create_dataset(dataset)
        print(f"Created dataset: {dataset_ref}")


def upload_and_load(bucket, bq_client, table_name, local_path):
    size_mb = os.path.getsize(local_path) / (1024 * 1024)
    blob_path = f"raw/{table_name}.csv"

    print(f"\n{table_name} ({size_mb:.1f} MB)")
    print(f"  Uploading to gs://{BUCKET_NAME}/{blob_path} ...")

    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path)

    table_id = f"{GCP_PROJECT_ID}.{DATASET_ID}.{table_name}"
    uri = f"gs://{BUCKET_NAME}/{blob_path}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        # Required: postings.csv has free-text fields (job descriptions)
        # containing embedded newlines inside quoted values.
        allow_quoted_newlines=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print(f"  Loading into {table_id} ...")
    load_job = bq_client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()  # wait for completion, raises on failure

    table = bq_client.get_table(table_id)
    print(f"  Done: {table.num_rows:,} rows loaded.")


def main():
    for var_name, val in [
        ("GCP_PROJECT_ID", GCP_PROJECT_ID),
        ("GCS_BUCKET_NAME", BUCKET_NAME),
        ("GOOGLE_APPLICATION_CREDENTIALS", CREDENTIALS_PATH),
    ]:
        if not val:
            raise RuntimeError(f"Missing {var_name} in .env")

    storage_client = storage.Client(project=GCP_PROJECT_ID)
    bq_client = bigquery.Client(project=GCP_PROJECT_ID)

    bucket = ensure_bucket(storage_client)
    ensure_dataset(bq_client)

    csv_files = find_csv_files(DATA_DIR)
    print(f"\nFound {len(csv_files)} CSV files to ingest.")

    for table_name, local_path in csv_files:
        upload_and_load(bucket, bq_client, table_name, local_path)

    print(f"\nAll done. Dataset: {GCP_PROJECT_ID}.{DATASET_ID}")


if __name__ == "__main__":
    main()