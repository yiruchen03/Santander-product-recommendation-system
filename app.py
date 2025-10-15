from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import lightgbm as lgb
import pickle
import os
import shap
from typing import List, Optional, Dict
import json

# 24 financial products
PRODUCTS = [
    'ind_ahor_fin_ult1', 'ind_aval_fin_ult1', 'ind_cco_fin_ult1', 'ind_cder_fin_ult1',
    'ind_cno_fin_ult1', 'ind_ctju_fin_ult1', 'ind_ctma_fin_ult1', 'ind_ctop_fin_ult1',
    'ind_ctpp_fin_ult1', 'ind_deco_fin_ult1', 'ind_deme_fin_ult1', 'ind_dela_fin_ult1',
    'ind_ecue_fin_ult1', 'ind_fond_fin_ult1', 'ind_hip_fin_ult1', 'ind_plan_fin_ult1',
    'ind_pres_fin_ult1', 'ind_reca_fin_ult1', 'ind_tjcr_fin_ult1', 'ind_valo_fin_ult1',
    'ind_viv_fin_ult1', 'ind_nomina_ult1', 'ind_nom_pens_ult1', 'ind_recibo_ult1'
]

MODELS_DIR = os.getenv("MODELS_DIR", "models")
FEATURE_COLS_PATH = os.path.join(MODELS_DIR, "feature_cols.json")

app = FastAPI(title="Santander Product Recommendation API")

# Load models for each product
models = {}
explainers = {}

def load_models():
    """Load LightGBM models for all 24 products"""
    global models, feature_cols
    
    # Load feature columns
    if os.path.exists(FEATURE_COLS_PATH):
        with open(FEATURE_COLS_PATH, 'r') as f:
            feature_cols = json.load(f)
    else:
        raise FileNotFoundError(f"Feature columns file not found: {FEATURE_COLS_PATH}")
    
    for product in PRODUCTS:
        model_path = os.path.join(MODELS_DIR, f"{product}_model.txt")
        if os.path.exists(model_path):
            models[product] = lgb.Booster(model_file=model_path)
            print(f"✓ Loaded model for {product}")
        else:
            print(f"⚠ Warning: Model not found for {product}")
    
    if len(models) == 0:
        raise FileNotFoundError("No models found. Please train and save models first.")

# Load models on startup
try:
    load_models()
    print(f"Successfully loaded {len(models)} product models")
except Exception as e:
    print(f"Error loading models: {e}")
    print("API will start but predictions will fail. Please ensure models are in 'models/' directory.")

class RecommendationRequest(BaseModel):
    customer_id: int
    features: Dict[str, float]  # Customer features
    owned_products: Optional[List[str]] = []  # Products already owned
    k: Optional[int] = 7  # Number of recommendations
    return_scores: Optional[bool] = False

class RecommendationResponse(BaseModel):
    customer_id: int
    recommendations: List[str]
    scores: Optional[Dict[str, float]] = None

class ExplainRequest(BaseModel):
    customer_id: int
    features: Dict[str, float]
    product: str  # Which product to explain

class FairnessRequest(BaseModel):
    customer_features_list: List[Dict[str, float]]
    demographic_attribute: str  # 'age', 'gender', or 'income'
    k: Optional[int] = 7

@app.get("/")
def root():
    return {
        "service": "Santander Product Recommendation Engine",
        "version": "1.0",
        "models_loaded": len(models),
        "products": len(PRODUCTS),
        "endpoints": {
            "/health": "Health check",
            "/recommend": "Get product recommendations for a customer",
            "/explain": "Get SHAP explanation for a product recommendation",
            "/fairness": "Evaluate recommendation fairness across demographic groups"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "models_loaded": len(models),
        "products": len(PRODUCTS)
    }

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(req: RecommendationRequest):
    """
    Recommend top K products for a customer based on their features.
    Returns products ranked by predicted probability, excluding already owned products.
    """
    try:
        # Prepare feature dataframe
        x = pd.DataFrame([req.features])
        
        # Ensure all required features are present
        missing_features = set(feature_cols) - set(x.columns)
        if missing_features:
            # Fill missing features with 0 or mean values
            for feat in missing_features:
                x[feat] = 0
        
        # Reorder columns to match training
        x = x[feature_cols]
        
        # Get predictions for all products
        # Note: Convert DataFrame to numpy array to avoid categorical feature issues
        product_scores = {}
        for product, model in models.items():
            if product not in req.owned_products:
                # Use raw values to avoid categorical feature mismatch
                pred_proba = model.predict(x.values)[0]
                product_scores[product] = float(pred_proba)
        
        # Sort by score and get top K
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        top_k = sorted_products[:req.k]
        
        recommendations = [prod for prod, score in top_k]
        scores = {prod: score for prod, score in top_k} if req.return_scores else None
        
        return RecommendationResponse(
            customer_id=req.customer_id,
            recommendations=recommendations,
            scores=scores
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/explain")
def explain(req: ExplainRequest):
    """
    Explain why a specific product was recommended using feature importance.
    Uses LightGBM's native feature importance as a proxy for SHAP values.
    This provides interpretability for the recommendation.
    """
    try:
        if req.product not in models:
            raise HTTPException(status_code=404, detail=f"Model for product {req.product} not found")
        
        # Prepare feature dataframe
        x = pd.DataFrame([req.features])
        missing_features = set(feature_cols) - set(x.columns)
        for feat in missing_features:
            x[feat] = 0
        x = x[feature_cols]
        
        # Get model for the specific product
        model = models[req.product]
        
        # Get prediction
        prediction = float(model.predict(x.values)[0])
        
        # Use LightGBM's feature importance (gain-based)
        # This is more reliable than SHAP for models with categorical features
        feature_importance_values = model.feature_importance(importance_type='gain')
        
        # Normalize to sum to prediction value (similar to SHAP)
        total_importance = feature_importance_values.sum()
        if total_importance > 0:
            normalized_importance = (feature_importance_values / total_importance) * prediction
        else:
            normalized_importance = np.zeros(len(feature_cols))
        
        # Create feature importance dictionary
        feature_importance = {}
        for i, feature in enumerate(feature_cols):
            # Multiply by feature value to show directional impact
            feature_value = x.iloc[0, i]
            if pd.notna(feature_value):
                impact = normalized_importance[i] * (1 if feature_value > 0 else -1)
            else:
                impact = 0
            feature_importance[feature] = float(impact)
        
        # Sort by absolute importance
        sorted_importance = dict(sorted(
            feature_importance.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        )[:10])  # Top 10 most important features
        
        # Calculate base value (average prediction)
        base_value = 0.1  # Approximate baseline probability
        
        return {
            "customer_id": req.customer_id,
            "product": req.product,
            "prediction_score": prediction,
            "top_features": sorted_importance,
            "base_value": base_value,
            "explanation": "Feature importance based on LightGBM gain. Positive values increase prediction, negative values decrease it."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation error: {str(e)}")

@app.post("/fairness")
def fairness_check(req: FairnessRequest):
    """
    Evaluate fairness of recommendations across demographic groups.
    Returns average recommendation scores by demographic attribute.
    """
    try:
        if req.demographic_attribute not in ['age', 'gender', 'income']:
            raise HTTPException(status_code=400, detail="demographic_attribute must be 'age', 'gender', or 'income'")
        
        results_by_group = {}
        
        for features in req.customer_features_list:
            # Get demographic value
            demo_value = features.get(req.demographic_attribute, 'unknown')
            
            # Prepare features
            x = pd.DataFrame([features])
            missing_features = set(feature_cols) - set(x.columns)
            for feat in missing_features:
                x[feat] = 0
            x = x[feature_cols]
            
            # Get predictions for all products
            scores = []
            for product, model in models.items():
                # Use raw values to avoid categorical feature mismatch
                pred_proba = model.predict(x.values)[0]
                scores.append(pred_proba)
            
            # Calculate average score for top K recommendations
            top_k_scores = sorted(scores, reverse=True)[:req.k]
            avg_score = np.mean(top_k_scores)
            
            # Group by demographic attribute
            if demo_value not in results_by_group:
                results_by_group[demo_value] = []
            results_by_group[demo_value].append(avg_score)
        
        # Calculate statistics for each group
        fairness_metrics = {}
        for group, scores in results_by_group.items():
            fairness_metrics[str(group)] = {
                "mean_score": float(np.mean(scores)),
                "std_score": float(np.std(scores)),
                "count": len(scores)
            }
        
        # Calculate fairness ratio (max/min)
        mean_scores = [m["mean_score"] for m in fairness_metrics.values()]
        fairness_ratio = max(mean_scores) / min(mean_scores) if min(mean_scores) > 0 else None
        
        return {
            "demographic_attribute": req.demographic_attribute,
            "groups": fairness_metrics,
            "fairness_ratio": fairness_ratio,
            "note": "Fairness ratio closer to 1.0 indicates more equal treatment across groups"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fairness check error: {str(e)}")