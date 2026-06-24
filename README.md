# Zameen.com Property Scraper & Price Predictor

A comprehensive machine learning project to scrape property data from [Zameen.com](https://www.zameen.com) and predict house prices in Islamabad using XGBoost. The project includes a fully integrated GUI for easy interaction.

## 🚀 Features

-   **Web Scraper:** Automated scraping of property listings (Price, Area, Bedrooms, Bathrooms, Location, Features).
-   **Data Processing:** Cleans and normalizes raw data for machine learning.
-   **Price Prediction:** Uses a trained XGBoost model to provide accurate price estimates for properties in Islamabad.
-   **Interactive GUI:** A user-friendly desktop application to perform predictions and trigger data updates.
-   **Confidence Interval:** Provides a price range (±10%) for every prediction.

## 📂 Project Structure

```text
.
├── main_gui.py           # Main Graphical User Interface
├── data/                 # Dataset storage (CSV files)
│   ├── zameen_islamabad.csv     # Scraped data
│   └── zameen_processed.csv     # Cleaned data for training
├── models/               # ML Models and Inference logic
│   ├── predict.py        # Inference logic and loading scripts
│   ├── xgboost.pkl       # Trained XGBoost model
│   ├── label_encoders.pkl# Preprocessing encoders
│   └── train_models.py   # Training script (supports RandomForest, CatBoost, etc.)
├── scraper/              # Scraping logic
│   ├── zameen_scraper.py # Core scraper (BS4 based)
│   └── generate_dataset.py
└── catboost_info/        # Metadata for CatBoost (if used)
```

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/zameen-scraper-ml.git
    cd Zameen.com_Scraper
    ```

2.  **Install dependencies:**
    ```bash
    pip install requests beautifulsoup4 pandas numpy xgboost scikit-learn
    ```

## 🎮 How to Run

### Graphical User Interface (Recommended)
Launch the desktop application to interact with the predictor:
```bash
python main_gui.py
```

### Command Line Interface
Run a direct prediction test:
```bash
python models/predict.py
```

### Run Scraper Manually
To update the dataset with the latest listings:
```bash
python scraper/zameen_scraper.py
```

## 🧠 Machine Learning Details

The system is trained on thousands of listings from Islamabad. Features used for prediction include:
-   **Location & Property Type** (Encoded via LabelEncoder)
-   **Area (sqft)** (Log-transformed for better distribution)
-   **Room counts** (Beds, Baths, Kitchens, etc.)
-   **Amenities** (Parking, Servant Quarter, Store Room)
-   **Property Age** (Calculated from Built Year)

The primary model used is **XGBoost Regressor**, chosen for its high performance on tabular real estate data.

## ⚠️ Disclaimer
This project is for educational purposes only. Web scraping should be done respectfully and in compliance with the website's Terms of Service and robots.txt.

---
**Author:** 
Saira Ahmed
