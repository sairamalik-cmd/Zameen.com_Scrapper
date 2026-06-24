"""
Machine Learning Model Training & Evaluation
House Price Prediction — Islamabad (Zameen.com)
Models: Linear Regression, Decision Tree, Random Forest,
        Gradient Boosting, XGBoost, CatBoost
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
import pickle
import warnings
warnings.filterwarnings("ignore")

from sklearn.linear_model    import LinearRegression
from sklearn.tree            import DecisionTreeRegressor
from sklearn.ensemble        import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics         import mean_absolute_error, mean_squared_error, r2_score
from xgboost                 import XGBRegressor
from catboost                import CatBoostRegressor

from preprocessing import run_preprocessing

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../models/")
os.makedirs(MODELS_DIR, exist_ok=True)

# ─── Metric Helper ─────────────────────────────────────────────────────────────

def evaluate(name, model, X_test, y_test, scaled=False):
    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    mse  = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2   = r2_score(y_test, y_pred)
    print(f"  {name:<28} MAE={mae:>12,.0f}  RMSE={rmse:>13,.0f}  R²={r2:.4f}")
    return {"Model": name, "MAE": mae, "MSE": mse, "RMSE": rmse, "R2": r2,
            "y_pred": y_pred.tolist()}


# ─── Model Definitions ─────────────────────────────────────────────────────────

def define_models():
    return {
        "Linear Regression": LinearRegression(),

        "Decision Tree": DecisionTreeRegressor(
            max_depth=8, min_samples_split=10,
            min_samples_leaf=5, random_state=42
        ),

        "Random Forest": RandomForestRegressor(
            n_estimators=200, max_depth=12,
            min_samples_split=5, min_samples_leaf=3,
            n_jobs=-1, random_state=42
        ),

        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=200, max_depth=5, learning_rate=0.08,
            subsample=0.8, random_state=42
        ),

        "XGBoost": XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=0.1, reg_lambda=1.0,
            random_state=42, verbosity=0
        ),

        "CatBoost": CatBoostRegressor(
            iterations=300, depth=6, learning_rate=0.05,
            l2_leaf_reg=3, random_seed=42, verbose=0
        ),
    }


# ─── Training Loop ─────────────────────────────────────────────────────────────

def train_and_evaluate(data):
    X_train         = data["X_train"]
    X_test          = data["X_test"]
    y_train         = data["y_train"]
    y_test          = data["y_test"]
    X_train_scaled  = data["X_train_scaled"]
    X_test_scaled   = data["X_test_scaled"]
    feature_cols    = data["feature_cols"]

    models = define_models()
    results = []
    trained_models = {}

    print("\n" + "="*75)
    print("MODEL TRAINING & EVALUATION")
    print("="*75)

    for name, model in models.items():
        print(f"\n[→] Training: {name}")

        # Linear Regression uses scaled features
        if name == "Linear Regression":
            model.fit(X_train_scaled, y_train)
            res = evaluate(name, model, X_test_scaled, y_test)
        else:
            model.fit(X_train, y_train)
            res = evaluate(name, model, X_test, y_test)

        results.append(res)
        trained_models[name] = model

        # Save model
        model_path = os.path.join(MODELS_DIR, f"{name.lower().replace(' ', '_')}.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

    # ─── Summary Table ─────────────────────────────────────────────────────────
    metrics_df = pd.DataFrame([{k: v for k, v in r.items() if k != "y_pred"} for r in results])
    metrics_df = metrics_df.sort_values("R2", ascending=False).reset_index(drop=True)

    print("\n" + "="*75)
    print("RESULTS SUMMARY (sorted by R²)")
    print("="*75)
    print(metrics_df.to_string(index=False, float_format="{:,.2f}".format))

    best_model_name = metrics_df.iloc[0]["Model"]
    best_r2         = metrics_df.iloc[0]["R2"]
    print(f"\n[★] BEST MODEL: {best_model_name}  (R² = {best_r2:.4f})")

    # Save metrics
    metrics_df.to_csv(os.path.join(MODELS_DIR, "model_metrics.csv"), index=False)

    # Feature importance for best tree-based model
    tree_models = ["Random Forest", "XGBoost", "Gradient Boosting", "CatBoost"]
    for tm in tree_models:
        if tm in trained_models and tm == best_model_name:
            fi = pd.Series(trained_models[tm].feature_importances_, index=feature_cols)
            fi = fi.sort_values(ascending=False)
            print(f"\nFeature Importances ({tm}):")
            for feat, imp in fi.items():
                bar = "█" * int(imp * 50)
                print(f"  {feat:<25} {imp:.4f}  {bar}")
            fi.to_csv(os.path.join(MODELS_DIR, "feature_importance.csv"))
            break

    return metrics_df, trained_models, results


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    data = run_preprocessing()
    metrics_df, trained_models, results = train_and_evaluate(data)
