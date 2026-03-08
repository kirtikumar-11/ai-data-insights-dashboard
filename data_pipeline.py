"""
Data Pipeline — Loads all CSV files from the data/ folder into PostgreSQL.

Usage:
    python data_pipeline.py

This script:
  1. Reads all 9 Olist e-commerce CSV files
  2. Translates product category names to English
  3. Loads them into PostgreSQL tables
  4. Creates the query_logs table for the application
"""
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
DATABASE_URL = os.getenv("DATABASE_URL")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Map CSV filenames → PostgreSQL table names
CSV_TABLE_MAP = {
    "customers.csv":                          "customers",
    "geolocation.csv":                        "geolocation",
    "order_items.csv":                        "order_items",
    "order_payments.csv":                     "order_payments",
    "order_reviews.csv":                      "order_reviews",
    "orders.csv":                             "orders",
    "products.csv":                           "products",
    "sellers.csv":                            "sellers",
    "product_category_name_translation.csv":  "product_categories",
}


def load_csv(filename: str) -> pd.DataFrame:
    """Read a CSV file from the data directory."""
    path = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(path, encoding="utf-8")
    # Clean column names: strip BOM, whitespace
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    return df


def enrich_products(products_df: pd.DataFrame, categories_df: pd.DataFrame) -> pd.DataFrame:
    """Merge product category English translations into products table."""
    merged = products_df.merge(
        categories_df,
        on="product_category_name",
        how="left",
    )
    # Use English name as the primary category column
    merged["product_category"] = merged["product_category_name_english"].fillna(
        merged["product_category_name"]
    )
    merged.drop(
        columns=["product_category_name", "product_category_name_english"],
        inplace=True,
        errors="ignore",
    )
    return merged


def create_query_logs_table(engine):
    """Create the query_logs table used by the backend app."""
    create_sql = text("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id              SERIAL PRIMARY KEY,
            question        TEXT NOT NULL,
            generated_sql   TEXT,
            execution_time  DOUBLE PRECISION,
            result_rows     INTEGER,
            status          VARCHAR(20) DEFAULT 'success',
            error_message   TEXT,
            timestamp       TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    with engine.begin() as conn:
        conn.execute(create_sql)
    print("✔ query_logs table ready")


def main():
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not set in .env")
        sys.exit(1)

    engine = create_engine(DATABASE_URL, echo=False)
    print(f"Connecting to database...")

    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✔ Database connection successful\n")
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        sys.exit(1)

    # Load all CSVs
    dataframes: dict[str, pd.DataFrame] = {}
    for csv_file, table_name in CSV_TABLE_MAP.items():
        print(f"  Loading {csv_file}...")
        dataframes[table_name] = load_csv(csv_file)
        print(f"    → {len(dataframes[table_name]):,} rows")

    # Enrich products with English category names
    print("\n  Enriching products with English category names...")
    dataframes["products"] = enrich_products(
        dataframes["products"],
        dataframes["product_categories"],
    )

    # Write each DataFrame to PostgreSQL
    print("\nWriting tables to PostgreSQL...")
    load_order = [
        "customers",
        "sellers",
        "geolocation",
        "product_categories",
        "products",
        "orders",
        "order_items",
        "order_payments",
        "order_reviews",
    ]

    for table_name in load_order:
        df = dataframes[table_name]
        print(f"  Writing {table_name} ({len(df):,} rows)...", end=" ")
        df.to_sql(
            table_name,
            engine,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=5000,
        )
        print("✔")

    # Create application tables
    print("\nCreating application tables...")
    create_query_logs_table(engine)

    # Print summary
    print("\n" + "=" * 50)
    print("DATA PIPELINE COMPLETE")
    print("=" * 50)
    with engine.connect() as conn:
        for table_name in load_order + ["query_logs"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"  {table_name:35s} → {count:>10,} rows")
    print("=" * 50)


if __name__ == "__main__":
    main()
