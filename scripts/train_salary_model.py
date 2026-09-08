"""
Job Market Intelligence - Stage 4: Salary prediction model
--------------------------------------------------------------------------
Trains a RandomForestRegressor to predict max_salary from job features
(experience level, location, company size, industry, and 15 in-demand
skill flags), using the mart_salary_features table built in dbt.

Random Forest chosen deliberately over a more complex model (e.g. a
neural network) because:
  - It handles the mix of categorical and numeric features without
    heavy preprocessing.
  - feature_importances_ gives a directly interpretable answer to
    "what actually drives salary here" -- appropriate for a business
    insight tool, not a black box.
  - At ~30K rows, it's the right level of model complexity; nothing
    here calls for deep learning.

Usage:
    python scripts/train_salary_model.py
"""

import os

import pandas as pd
import numpy as np
from dotenv import load_dotenv
from google.cloud import bigquery
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

MODEL_OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "models_ml", "salary_model.joblib"
)

CATEGORICAL_FEATURES = ["experience_level", "work_type", "state", "primary_industry"]
NUMERIC_FEATURES = ["remote_allowed", "employee_count"]
SKILL_FEATURES = [
    "has_python", "has_sql", "has_aws", "has_cloud", "has_java", "has_excel",
    "has_docker", "has_kubernetes", "has_azure", "has_react", "has_javascript",
    "has_agile", "has_spark", "has_machine_learning", "has_data_engineering",
]
TARGET = "max_salary"


def fetch_data():
    client = bigquery.Client(project=GCP_PROJECT_ID)
    query = f"SELECT * FROM `{GCP_PROJECT_ID}.dbt_dev_marts.mart_salary_features`"
    print("Fetching training data from BigQuery...")
    df = client.query(query).to_dataframe()
    print(f"Loaded {len(df):,} rows.")
    return df


def main():
    df = fetch_data()

    # Basic cleaning: remote_allowed has real nulls (confirmed in Stage 0 --
    # it's a "flag only set when true" field, not a proper boolean), so
    # treat missing as 0 (not explicitly marked remote) rather than
    # dropping rows over it.
    df["remote_allowed"] = df["remote_allowed"].fillna(0)
    df["employee_count"] = df["employee_count"].fillna(df["employee_count"].median())
    df["state"] = df["state"].fillna("Unknown")
    df["primary_industry"] = df["primary_industry"].fillna("Unknown")
    df["experience_level"] = df["experience_level"].fillna("Unknown")
    df["work_type"] = df["work_type"].fillna("Unknown")

    # BigQuery's to_dataframe() returns nullable extension dtypes (e.g.
    # pandas "Int64" with a capital I, which can carry pandas.NA even
    # after fillna) for INT64/numeric columns. scikit-learn's internals
    # don't handle that extension type cleanly -- cast everything numeric
    # to plain float64 explicitly to sidestep it.
    for col in NUMERIC_FEATURES + SKILL_FEATURES:
        df[col] = df[col].astype("float64")

    # Basic outlier guard: a handful of postings will have implausible
    # salary values (data entry errors in the source, e.g. $5 or $50M).
    # Clip to a reasonable range rather than silently trusting every value.
    before = len(df)
    df = df[(df[TARGET] >= 20000) & (df[TARGET] <= 500000)]
    print(f"Dropped {before - len(df)} rows with implausible salary values (outside $20K-$500K).")

    feature_cols = CATEGORICAL_FEATURES + NUMERIC_FEATURES + SKILL_FEATURES
    X = df[feature_cols]
    y = df[TARGET]

    # Salary is right-skewed (a small number of very high salaries stretch
    # the distribution) -- training on log(salary) instead of raw salary
    # is the standard fix for this and usually improves regression
    # performance meaningfully. Metrics are still reported in real dollars
    # by inverse-transforming predictions back (np.expm1) before scoring,
    # so results stay interpretable to a non-technical audience.
    y_log = np.log1p(y)

    X_train, X_test, y_train_log, y_test_log = train_test_split(X, y_log, test_size=0.2, random_state=42)
    print(f"Train: {len(X_train):,} rows | Test: {len(X_test):,} rows")

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", max_categories=30), CATEGORICAL_FEATURES),
        ],
        remainder="passthrough",  # numeric + skill flag columns pass through unchanged
    )

    model = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)),
    ])

    print("\nTraining RandomForestRegressor (on log-transformed salary)...")
    model.fit(X_train, y_train_log)

    y_pred_log = model.predict(X_test)
    # Inverse-transform back to real dollars for interpretable metrics.
    y_pred = np.expm1(y_pred_log)
    y_test = np.expm1(y_test_log)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n{'='*50}")
    print(f"Model performance on held-out test set:")
    print(f"  Mean Absolute Error: ${mae:,.0f}")
    print(f"  R-squared:           {r2:.3f}")
    print(f"{'='*50}\n")

    # Feature importances -- the interpretable payoff of this model choice
    ohe_feature_names = model.named_steps["preprocess"].named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES)
    all_feature_names = list(ohe_feature_names) + NUMERIC_FEATURES + SKILL_FEATURES
    importances = model.named_steps["regressor"].feature_importances_

    importance_df = pd.DataFrame({
        "feature": all_feature_names,
        "importance": importances,
    }).sort_values("importance", ascending=False)

    print("Top 15 most important features for predicting salary:")
    print(importance_df.head(15).to_string(index=False))

    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_PATH)
    print(f"\nModel saved to {os.path.normpath(MODEL_OUTPUT_PATH)}")


if __name__ == "__main__":
    main()