"""
Data Preprocessing Pipeline
House Price Prediction — Zameen.com Islamabad Dataset
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import os
import pickle

DATA_PATH   = os.path.join(os.path.dirname(__file__), "../data/zameen_islamabad.csv")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "../data/")
MODELS_DIR  = os.path.join(os.path.dirname(__file__), "../models/")
os.makedirs(MODELS_DIR, exist_ok=True)


def load_data():
    df = pd.read_csv(DATA_PATH)
    print(f"[1] Loaded dataset: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


def remove_duplicates(df):
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    print(f"[2] Removed {removed} duplicate rows → {len(df)} remaining")
    return df


def handle_missing_values(df):
    print(f"[3] Missing values before:")
    print(df.isnull().sum()[df.isnull().sum() > 0].to_string())

    # Built-in year: fill with median
    df["built_in_year"] = df["built_in_year"].fillna(df["built_in_year"].median())
    df["built_in_year"] = df["built_in_year"].astype(int)

    # Parking spaces: fill with mode
    df["parking_spaces"] = df["parking_spaces"].fillna(df["parking_spaces"].mode()[0])
    df["parking_spaces"] = df["parking_spaces"].astype(int)

    # Drawing rooms: fill with 0
    df["drawing_rooms"] = df["drawing_rooms"].fillna(0).astype(int)

    print(f"    → Missing values after: {df.isnull().sum().sum()}")
    return df


def clean_outliers(df):
    before = len(df)
    # Remove properties with price < 500k or > 500M (likely errors)
    df = df[(df["price"] >= 500_000) & (df["price"] <= 500_000_000)]
    # Remove unrealistic areas
    df = df[(df["area_sqft"] >= 200) & (df["area_sqft"] <= 50_000)]
    # Remove impossible bedroom/bathroom counts
    df = df[(df["bedrooms"] >= 1) & (df["bedrooms"] <= 15)]
    df = df[(df["bathrooms"] >= 1) & (df["bathrooms"] <= 15)]
    print(f"[4] Removed {before - len(df)} outlier rows → {len(df)} remaining")
    return df


def feature_engineering(df):
    # Age of property
    df["property_age"] = 2024 - df["built_in_year"]

    # Price per sqft (for analysis only, not used as feature to avoid leakage)
    # Total rooms
    df["total_rooms"] = df["bedrooms"] + df["bathrooms"] + df["drawing_rooms"] + df["kitchens"]

    # Luxury flag (servant quarters OR farm house)
    df["is_luxury"] = ((df["servant_quarters"] == 1) | (df["property_type"] == "Farm House")).astype(int)

    # Log transform area (reduces skew)
    df["log_area"] = np.log1p(df["area_sqft"])

    print(f"[5] Feature engineering complete. New columns: property_age, total_rooms, is_luxury, log_area")
    return df


def encode_categoricals(df):
    label_encoders = {}

    categorical_cols = ["location", "property_type", "city"]

    for col in categorical_cols:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
        print(f"[6] Encoded '{col}': {len(le.classes_)} unique values")

    # Save encoders
    with open(os.path.join(MODELS_DIR, "label_encoders.pkl"), "wb") as f:
        pickle.dump(label_encoders, f)

    return df, label_encoders


def select_features(df):
    feature_cols = [
        "area_sqft",
        "log_area",
        "bedrooms",
        "bathrooms",
        "parking_spaces",
        "servant_quarters",
        "store_rooms",
        "kitchens",
        "drawing_rooms",
        "property_age",
        "total_rooms",
        "is_luxury",
        "location_enc",
        "property_type_enc",
    ]
    target_col = "price"

    X = df[feature_cols]
    y = df[target_col]
    print(f"[7] Features selected: {feature_cols}")
    print(f"    Target: {target_col}")
    return X, y, feature_cols


def split_and_scale(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"[8] Train/Test split: {len(X_train)} train | {len(X_test)} test (80/20)")

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    # Save scaler
    with open(os.path.join(MODELS_DIR, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    print(f"    Scaler saved.")
    return X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled, scaler


def run_preprocessing():
    df = load_data()
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = clean_outliers(df)
    df = feature_engineering(df)
    df, label_encoders = encode_categoricals(df)
    X, y, feature_cols = select_features(df)
    X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled, scaler = split_and_scale(X, y)

    # Save processed dataset
    df.to_csv(os.path.join(OUTPUT_DIR, "zameen_processed.csv"), index=False)
    print(f"\n[✓] Preprocessing complete. Processed CSV saved.")

    return {
        "df": df,
        "X_train": X_train, "X_test": X_test,
        "y_train": y_train, "y_test": y_test,
        "X_train_scaled": X_train_scaled, "X_test_scaled": X_test_scaled,
        "scaler": scaler, "label_encoders": label_encoders,
        "feature_cols": feature_cols,
    }


if __name__ == "__main__":
    data = run_preprocessing()
    print("\nProcessed DataFrame head:")
    print(data["df"][["price","area_sqft","location","property_type","bedrooms","property_age"]].head())
