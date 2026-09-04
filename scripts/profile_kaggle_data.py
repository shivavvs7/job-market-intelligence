"""
Job Market Intelligence - Stage 0: Kaggle dataset discovery/profiling
-----------------------------------------------------------------------
Profiles every CSV in data/raw/ (and its subfolders): row counts, columns,
dtypes, and null rates. Reads large files in chunks rather than loading
them fully into memory -- postings.csv alone is ~516MB.

Usage:
    python scripts/profile_kaggle_data.py
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "kaggle_discovery_report.md")
CHUNK_SIZE = 100_000


def find_csv_files(root):
    csv_files = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(".csv"):
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, root)
                csv_files.append((rel_path, full_path))
    return sorted(csv_files)


def profile_csv(path, chunk_size=CHUNK_SIZE):
    """Stream through a CSV in chunks, accumulating row count and null counts per column."""
    total_rows = 0
    null_counts = None
    dtypes = None
    columns = None

    for chunk in pd.read_csv(path, chunksize=chunk_size, low_memory=False, on_bad_lines="skip"):
        if columns is None:
            columns = list(chunk.columns)
            null_counts = {col: 0 for col in columns}
            dtypes = {col: str(chunk[col].dtype) for col in columns}

        total_rows += len(chunk)
        for col in columns:
            null_counts[col] += chunk[col].isna().sum()

    null_pcts = {
        col: round(100 * null_counts[col] / total_rows, 1) if total_rows else 0.0
        for col in columns
    }

    return {
        "total_rows": total_rows,
        "columns": columns,
        "dtypes": dtypes,
        "null_pcts": null_pcts,
    }


def main():
    csv_files = find_csv_files(DATA_DIR)
    print(f"Found {len(csv_files)} CSV files under {DATA_DIR}\n")

    report_lines = ["# Kaggle LinkedIn Job Postings - Discovery Report\n"]
    report_lines.append(f"Source: `arshkon/linkedin-job-postings` (Kaggle, CC-BY-SA-4.0)\n")

    for rel_path, full_path in csv_files:
        size_mb = os.path.getsize(full_path) / (1024 * 1024)
        print(f"Profiling {rel_path} ({size_mb:.1f} MB)...")

        profile = profile_csv(full_path)

        report_lines.append(f"\n---\n\n## `{rel_path}`\n")
        report_lines.append(f"- File size: {size_mb:.1f} MB")
        report_lines.append(f"- Row count: {profile['total_rows']:,}")
        report_lines.append(f"\n| Column | Dtype | Null % |")
        report_lines.append(f"|---|---|---|")
        for col in profile["columns"]:
            report_lines.append(
                f"| `{col}` | {profile['dtypes'][col]} | {profile['null_pcts'][col]}% |"
            )

        print(f"  -> {profile['total_rows']:,} rows, {len(profile['columns'])} columns")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\nDone. Report written to {os.path.normpath(OUTPUT_PATH)}")


if __name__ == "__main__":
    main()
