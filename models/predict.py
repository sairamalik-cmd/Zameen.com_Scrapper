"""
House Price Prediction System
Zameen.com Islamabad — Final Inference Interface
"""

import os, sys, pickle, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(__file__))

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../models/")

LOCATIONS = [
    "DHA Phase 1","DHA Phase 2","F-6","F-7","F-8","F-10","F-11",
    "G-6","G-8","G-9","G-10","G-11","G-13","G-14","G-15",
    "I-8","I-10","E-11","B-17","Bahria Town Phase 1",
    "Bahria Town Phase 4","Bahria Town Phase 7","Gulberg Residencia",
    "PWD Housing Society","Margalla Town","Chak Shahzad",
    "Bhara Kahu","Tarlai","Koral Town","Rawat",
]
PROPERTY_TYPES = ["House","Apartment","Upper Portion","Lower Portion","Farm House"]


def load_artifacts():
    with open(os.path.join(MODELS_DIR, "xgboost.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(MODELS_DIR, "label_encoders.pkl"), "rb") as f:
        encoders = pickle.load(f)
    return model, encoders


def format_pkr(price):
    if price >= 1e7:
        return f"PKR {price/1e7:.2f} Crore"
    elif price >= 1e5:
        return f"PKR {price/1e5:.2f} Lakh"
    else:
        return f"PKR {price:,.0f}"


def build_feature_vector(inputs, encoders):
    area      = inputs["area_sqft"]
    beds      = inputs["bedrooms"]
    baths     = inputs["bathrooms"]
    location  = inputs["location"]
    prop_type = inputs["property_type"]
    parking   = inputs.get("parking_spaces", 1)
    servant_q = inputs.get("servant_quarters", 0)
    store_r   = inputs.get("store_rooms", 0)
    kitchens  = inputs.get("kitchens", 1)
    drawing_r = inputs.get("drawing_rooms", 0)
    built_yr  = inputs.get("built_in_year", 2010)

    property_age = 2024 - int(built_yr)
    log_area     = np.log1p(area)
    total_rooms  = beds + baths + drawing_r + kitchens
    is_luxury    = 1 if (servant_q == 1 or prop_type == "Farm House") else 0

    loc_enc  = encoders["location"].transform([location])[0]
    pt_enc   = encoders["property_type"].transform([prop_type])[0]

    features = np.array([[
        area, log_area, beds, baths, parking, servant_q, store_r,
        kitchens, drawing_r, property_age, total_rooms, is_luxury,
        loc_enc, pt_enc
    ]])
    return features


def predict_price(inputs):
    model, encoders = load_artifacts()
    X = build_feature_vector(inputs, encoders)
    price = model.predict(X)[0]
    # Confidence range ±10%
    low  = price * 0.90
    high = price * 1.10
    return price, low, high


def run_interactive():
    print("\n" + "="*60)
    print("   🏠  ISLAMABAD HOUSE PRICE PREDICTOR")
    print("   Powered by XGBoost — Trained on Zameen.com Data")
    print("="*60)

    # Location
    print("\nAvailable Locations:")
    for i, loc in enumerate(LOCATIONS, 1):
        print(f"  {i:>2}. {loc}")
    loc_idx = int(input("\nEnter location number: ").strip()) - 1
    location = LOCATIONS[loc_idx]

    # Property type
    print("\nProperty Types:")
    for i, pt in enumerate(PROPERTY_TYPES, 1):
        print(f"  {i}. {pt}")
    pt_idx = int(input("Enter property type number: ").strip()) - 1
    prop_type = PROPERTY_TYPES[pt_idx]

    area     = float(input("Area (sq. ft.): ").strip())
    bedrooms = int(input("Number of Bedrooms: ").strip())
    bathrooms= int(input("Number of Bathrooms: ").strip())
    parking  = int(input("Parking Spaces (0-3): ").strip())
    built_yr = int(input("Year Built (e.g. 2010): ").strip())

    servant_q= int(input("Servant Quarters? (1=Yes, 0=No): ").strip())
    store_r  = int(input("Store Rooms (0-2): ").strip())

    inputs = {
        "area_sqft": area,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "location": location,
        "property_type": prop_type,
        "parking_spaces": parking,
        "built_in_year": built_yr,
        "servant_quarters": servant_q,
        "store_rooms": store_r,
        "kitchens": 1,
        "drawing_rooms": 0,
    }

    price, low, high = predict_price(inputs)

    print("\n" + "─"*60)
    print(f"  📍 Location     : {location}")
    print(f"  🏘  Property    : {prop_type}")
    print(f"  📐 Area         : {area:,.0f} sq. ft.")
    print(f"  🛏  Bedrooms    : {bedrooms}")
    print(f"  🚿 Bathrooms    : {bathrooms}")
    print(f"  📅 Year Built   : {built_yr}")
    print("─"*60)
    print(f"\n  💰 ESTIMATED PRICE  : {format_pkr(price)}")
    print(f"     Price Range      : {format_pkr(low)}  –  {format_pkr(high)}")
    print("\n" + "─"*60)


def demo_predictions():
    """Show several example predictions."""
    model, encoders = load_artifacts()

    test_cases = [
        {"area_sqft":1500,"bedrooms":3,"bathrooms":3,"location":"G-13","property_type":"House","parking_spaces":1,"built_in_year":2015,"servant_quarters":0,"store_rooms":1,"kitchens":1,"drawing_rooms":0},
        {"area_sqft":3500,"bedrooms":5,"bathrooms":4,"location":"F-10","property_type":"House","parking_spaces":2,"built_in_year":2008,"servant_quarters":1,"store_rooms":2,"kitchens":1,"drawing_rooms":1},
        {"area_sqft":900,"bedrooms":2,"bathrooms":2,"location":"Bahria Town Phase 4","property_type":"Apartment","parking_spaces":1,"built_in_year":2019,"servant_quarters":0,"store_rooms":0,"kitchens":1,"drawing_rooms":0},
        {"area_sqft":7000,"bedrooms":7,"bathrooms":6,"location":"F-7","property_type":"House","parking_spaces":3,"built_in_year":2005,"servant_quarters":1,"store_rooms":2,"kitchens":2,"drawing_rooms":1},
        {"area_sqft":600,"bedrooms":2,"bathrooms":2,"location":"Rawat","property_type":"Upper Portion","parking_spaces":0,"built_in_year":2018,"servant_quarters":0,"store_rooms":0,"kitchens":1,"drawing_rooms":0},
    ]

    print("\n" + "="*70)
    print("SAMPLE PREDICTIONS")
    print("="*70)
    print(f"{'Location':<26} {'Type':<16} {'Area':>8} {'Beds':>5}  {'Predicted Price'}")
    print("-"*70)

    for tc in test_cases:
        X = build_feature_vector(tc, encoders)
        price = model.predict(X)[0]
        print(f"{tc['location']:<26} {tc['property_type']:<16} {tc['area_sqft']:>7.0f}  {tc['bedrooms']:>4}  {format_pkr(price)}")

    print("="*70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run demo predictions")
    args = parser.parse_args()

    if args.demo:
        demo_predictions()
    else:
        run_interactive()
