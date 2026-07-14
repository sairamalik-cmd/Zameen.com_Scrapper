# Zameen.com Property Scraper & Price Predictor
A comprehensive machine learning project to scrape property data from [Zameen.com](https://www.zameen.com) and predict house prices in Islamabad using XGBoost. The project also includes a fully integrated GUI for easy interaction.
## 🚀 Features
-   **Web Scraper:** Automated scraping of property listings (Price, Area, Bedrooms, Bathrooms, Location, Features).
-   **Data Processing:** Cleans and normalizes raw data for machine learning.
-   **Price Prediction:** Uses a trained XGBoost model to provide accurate price estimates for properties in Islamabad.
-   **Interactive GUI:** A user-friendly desktop application to perform predictions and trigger data updates.
-   **Confidence Interval:** Provides a price range (±10%) for every prediction.

### 🖥️ Desktop GUI — Price Predictor

<img width="400" alt="Price Predictor GUI image" src="https://github.com/user-attachments/assets/5d1fd319-f9ee-4996-8978-a3f84e4a60eb" />

---

## 📂 Project Structure
```text
.
├── main_gui.py           # Main Graphical User Interface
├── data/                 # Dataset storage (CSV files)
│   ├── zameen_islamabad.csv     # Scraped data
│   └── zameen_processed.csv     # Cleaned data for training
├── models/               # ML Models and Inference logic
│   ├── predict.py        # Inference and prediction logic
│   ├── preprocessing.py  # Data cleaning pipeline
│   └── train_models.py   # Training script (XGBoost, CatBoost, RF, etc.)
├── scraper/              # Scraping logic
│   ├── zameen_scraper.py # Core scraper (BS4 based)
│   └── generate_dataset.py
└── catboost_info/        # Metadata for CatBoost (if used)
```
## 🛠️ Installation
1.  **Clone the repository:**
```bash
    git clone https://github.com/sairamalik-cmd/Zameen.com_Scrapper.git
    cd Zameen.com_Scrapper
```
2.  **Install dependencies:**
```bash
    pip install requests beautifulsoup4 pandas numpy xgboost scikit-learn catboost matplotlib seaborn selenium
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
The system is trained on 387 listings from Islamabad. Features used for prediction include:
-   **Location & Property Type** (Encoded via LabelEncoder)
-   **Area (sqft)** (Log-transformed for better distribution)
-   **Room counts** (Beds, Baths, Kitchens, etc.)
-   **Amenities** (Parking, Servant Quarter, Store Room)
-   **Property Age** (Calculated from Built Year)
-   **Derived Features** (Total Rooms, Luxury Flag)

### Models Trained & Compared
Six regression algorithms were trained and evaluated on the same dataset:

| Model | MAE (PKR) | RMSE (PKR) | R² Score |
|---|---|---|---|
| XGBoost ⭐ | 2,484,707 | 5,188,850 | **0.8756** |
| Gradient Boosting | 2,597,797 | 5,581,414 | 0.8560 |
| CatBoost | 2,756,145 | 5,677,907 | 0.8510 |
| Random Forest | 3,478,812 | 6,854,443 | 0.7829 |
| Decision Tree | 4,211,342 | 8,750,797 | 0.6461 |
| Linear Regression | 5,541,378 | 9,309,913 | 0.5995 |


<img width="850" alt="Model Performance" src="https://github.com/user-attachments/assets/4c7990a5-2972-4dbe-81e2-130c059b5517" />

<img width="470" alt="XGBoost Actual vs Predicted" src="https://github.com/user-attachments/assets/93e604d7-8dbd-4c2e-aebc-3daedbeccbe8" />



The primary model used is **XGBoost Regressor**, chosen for its highest R² score of **0.8756**, meaning it explains 87.56% of the variance in house prices across Islamabad localities.

> ⚠️ **Disclaimer:** This project is for educational purposes only. Web scraping should be done respectfully and in compliance with the website's Terms of Service and robots.txt.

---

# Author
**Saira Ahmed** 
