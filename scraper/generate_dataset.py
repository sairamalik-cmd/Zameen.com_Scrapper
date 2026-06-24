"""
Dataset Generator for Islamabad House Prices
Generates a realistic synthetic dataset mirroring Zameen.com listing patterns
for the city of Islamabad, Pakistan.
"""

import pandas as pd
import numpy as np
import os
import random
from datetime import datetime

random.seed(42)
np.random.seed(42)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/zameen_islamabad.csv")

# ─── Islamabad-specific reference data ────────────────────────────────────────

LOCATIONS = {
    "DHA Phase 1":       {"base_price": 9000, "tier": "premium"},
    "DHA Phase 2":       {"base_price": 8500, "tier": "premium"},
    "F-6":               {"base_price": 12000,"tier": "ultra"},
    "F-7":               {"base_price": 11000,"tier": "ultra"},
    "F-8":               {"base_price": 10000,"tier": "ultra"},
    "F-10":              {"base_price": 9500, "tier": "premium"},
    "F-11":              {"base_price": 9000, "tier": "premium"},
    "G-6":               {"base_price": 7000, "tier": "high"},
    "G-8":               {"base_price": 6500, "tier": "high"},
    "G-9":               {"base_price": 6000, "tier": "high"},
    "G-10":              {"base_price": 6800, "tier": "high"},
    "G-11":              {"base_price": 6200, "tier": "high"},
    "G-13":              {"base_price": 5500, "tier": "mid"},
    "G-14":              {"base_price": 5000, "tier": "mid"},
    "G-15":              {"base_price": 4800, "tier": "mid"},
    "I-8":               {"base_price": 5800, "tier": "mid"},
    "I-10":              {"base_price": 5200, "tier": "mid"},
    "E-11":              {"base_price": 8000, "tier": "high"},
    "B-17":              {"base_price": 4200, "tier": "mid"},
    "Bahria Town Phase 1":{"base_price":6500, "tier": "high"},
    "Bahria Town Phase 4":{"base_price":7000, "tier": "high"},
    "Bahria Town Phase 7":{"base_price":7500, "tier": "high"},
    "Gulberg Residencia": {"base_price":5500, "tier": "mid"},
    "PWD Housing Society":{"base_price":4500, "tier": "mid"},
    "Margalla Town":     {"base_price": 4000, "tier": "mid"},
    "Chak Shahzad":      {"base_price": 3500, "tier": "low"},
    "Bhara Kahu":        {"base_price": 2800, "tier": "low"},
    "Tarlai":            {"base_price": 2500, "tier": "low"},
    "Koral Town":        {"base_price": 3000, "tier": "low"},
    "Rawat":             {"base_price": 2200, "tier": "low"},
}

PROPERTY_TYPES = ["House", "Apartment", "Upper Portion", "Lower Portion", "Farm House"]
PROPERTY_WEIGHTS = [0.45, 0.25, 0.12, 0.10, 0.08]

AREA_SIZES_BY_TYPE = {
    "House":          (500, 8000),
    "Apartment":      (400, 3000),
    "Upper Portion":  (300, 2000),
    "Lower Portion":  (300, 2000),
    "Farm House":     (3000, 20000),
}

BED_BATH_BY_AREA = [
    (0,    600,  1, 2, 1, 2),
    (601,  1000, 2, 3, 2, 3),
    (1001, 1800, 3, 4, 2, 4),
    (1801, 3000, 4, 5, 3, 5),
    (3001, 6000, 5, 7, 4, 6),
    (6001, 99999,6, 9, 5, 8),
]


def get_beds_baths(area):
    for (amin, amax, bmin, bmax, btmin, btmax) in BED_BATH_BY_AREA:
        if amin <= area <= amax:
            beds = random.randint(bmin, bmax)
            baths = random.randint(btmin, min(btmax, beds + 1))
            return beds, baths
    return 3, 2


def generate_price(area, location, prop_type, beds, year_built):
    loc_data = LOCATIONS[location]
    base_per_sqft = loc_data["base_price"]

    # Adjustments
    if prop_type == "Apartment":
        base_per_sqft *= 0.85
    elif prop_type in ("Upper Portion", "Lower Portion"):
        base_per_sqft *= 0.70
    elif prop_type == "Farm House":
        base_per_sqft *= 0.60

    # Age discount
    if year_built:
        age = 2024 - year_built
        base_per_sqft *= max(0.60, 1 - age * 0.01)

    base_price = area * base_per_sqft

    # Random market noise ±15%
    noise = random.uniform(0.85, 1.15)
    price = base_price * noise

    # Round to nearest 50,000
    return int(round(price / 50000) * 50000)


def generate_dataset(n=380):
    records = []
    locations = list(LOCATIONS.keys())
    location_weights = [1.0 / len(locations)] * len(locations)

    for i in range(n):
        location = random.choices(locations, weights=location_weights, k=1)[0]
        prop_type = random.choices(PROPERTY_TYPES, weights=PROPERTY_WEIGHTS, k=1)[0]

        # Area
        amin, amax = AREA_SIZES_BY_TYPE[prop_type]
        area = round(random.uniform(amin, amax), 2)

        # Beds & baths
        beds, baths = get_beds_baths(area)

        # Year built
        if random.random() < 0.70:
            year_built = random.randint(1990, 2023)
        else:
            year_built = None

        # Price
        price = generate_price(area, location, prop_type, beds, year_built)

        # Amenities (scaled with size)
        parking    = random.randint(0, min(3, beds))
        servant_q  = 1 if (beds >= 4 and random.random() > 0.4) else 0
        store_rooms= random.randint(0, 2) if area > 1000 else 0
        kitchens   = 1 if area < 2000 else random.randint(1, 2)
        drawing_r  = random.randint(0, 1) if beds >= 3 else 0

        records.append({
            "price":            price,
            "area_sqft":        area,
            "city":             "Islamabad",
            "bedrooms":         beds,
            "bathrooms":        baths,
            "location":         location,
            "property_type":    prop_type,
            "built_in_year":    year_built,
            "parking_spaces":   parking,
            "servant_quarters": servant_q,
            "store_rooms":      store_rooms,
            "kitchens":         kitchens,
            "drawing_rooms":    drawing_r,
        })

    df = pd.DataFrame(records)

    # Add ~5% missing values realistically
    for col in ["built_in_year", "parking_spaces", "drawing_rooms"]:
        mask = np.random.random(len(df)) < 0.05
        df.loc[mask, col] = np.nan

    # Add ~2% duplicates
    dup_count = int(0.02 * n)
    dup_rows = df.sample(dup_count)
    df = pd.concat([df, dup_rows], ignore_index=True)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"[✓] Dataset generated: {len(df)} rows → {OUTPUT_PATH}")
    print(df.describe().T.to_string())
    return df


if __name__ == "__main__":
    df = generate_dataset(380)
    print("\nSample rows:")
    print(df.head(10).to_string())
