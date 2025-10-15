# Santander Product Recommendation System

A large-scale financial product recommendation engine built with LightGBM, featuring model interpretability analysis, fairness testing, and containerized deployment with Docker.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![LightGBM](https://img.shields.io/badge/LightGBM-3.3-orange.svg)](https://lightgbm.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Key Features

- ✅ **Large-Scale Recommendation Engine**: Processes 10M+ customer records using LightGBM to predict cross-sell opportunities across 24 financial products
- ✅ **High Performance**: Achieves MAP@7 of 0.0147 with hybrid recommendation system
- ✅ **Model Interpretability**: Utilizes feature importance analysis to explain recommendation results
- ✅ **Fairness Testing**: Evaluates recommendation quality across demographic groups (age, gender, income)
- ✅ **End-to-End Deployment**: FastAPI + Docker containerization providing complete ML workflow from preprocessing to inference
- ✅ **Interactive Visualizations**: Uses matplotlib and seaborn to display feature importance and recommendation results

---

## 📊 Project Overview

This project demonstrates an end-to-end machine learning solution for financial product recommendations:

- **Dataset**: Santander Product Recommendation (Kaggle)
- **Scale**: 10M+ customer records, 18 months of historical data
- **Products**: 24 different financial products
- **Model**: 21 LightGBM binary classifiers (one per product)
- **Performance**: MAP@7 = 0.0147, Average AUC = 0.85
- **Deployment**: Production-ready FastAPI service with Docker support

---

## 🏗️ Project Structure

```
santander-product-recommendation/
├── 📓 Notebooks
│   ├── Santander_Recommendation_System4.ipynb  # Main training notebook
│   └── Santander_Recommendation_System3.ipynb  # Previous version
│
├── 🚀 Deployment
│   ├── app.py                      # FastAPI recommendation service
│   ├── predict_client.py           # API test client
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Docker configuration
│   ├── deploy.sh                   # Automated deployment script
│   └── start_api.sh               # API startup script
│
├── 📦 Models (generated after training)
│   ├── models/
│   │   ├── ind_*_model.txt        # 21 LightGBM models (one per product)
│   │   ├── feature_cols.json      # Feature list
│   │   ├── products.json          # Product list
│   │   ├── config.json            # Configuration and optimal parameters
│   │   └── metrics.json           # Model performance metrics
│
├── 📚 Documentation
│   ├── README.md                   # This file
│   ├── DEPLOYMENT.md              # Detailed deployment guide
│   ├── MODEL_IMPROVEMENTS.md      # Model optimization suggestions
│   ├── PROJECT_SUMMARY.md         # Project summary
│   ├── IMPROVED_CELLS.md          # Enhanced code cells
│   └── QUICK_START.md             # Quick start guide
│
└── 📊 Data
    ├── train_ver2.csv.zip         # Training data
    ├── test_ver2.csv.zip          # Test data
    └── sample_submission.csv.zip  # Sample submission
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- 8GB+ RAM (recommended)
- 2GB+ free disk space

### Step 1: Install Dependencies

```bash
# Clone the repository
cd santander-product-recommendation

# Install required packages
pip install -r requirements.txt

# For Mac users: Install OpenMP (required for LightGBM)
conda install -y lightgbm -c conda-forge
```

**Main Dependencies:**
- FastAPI & Uvicorn (API service)
- LightGBM (model training and inference)
- SHAP (model interpretability)
- Pandas, NumPy, Scikit-learn (data processing)
- Matplotlib, Seaborn (visualization)

### Step 2: Train Models

Open and run the main notebook:

```bash
jupyter notebook Santander_Recommendation_System4.ipynb
```

**Training Pipeline:**
1. **Data Loading**: Load and preprocess 10M+ customer records
2. **Feature Engineering**: Create user features and product history features
3. **Model Training**: Train 21 LightGBM binary classifiers (one per product)
4. **Hybrid System**: Combine model predictions with popularity priors
5. **Fairness Testing**: Evaluate recommendation quality across demographic groups
6. **Model Saving**: Run the last cell to save all models to `models/` directory

**Performance Metrics:**
- Model-only MAP@7: 0.0141
- Hybrid system MAP@7: 0.0147 (alpha=0.5)
- Average AUC: ~0.85 across 21 products

### Step 3: Start API Service

#### Option A: Local Development Mode

```bash
# Quick start (recommended for testing)
./deploy.sh --local

# Or manually
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### Option B: Docker Production Mode

```bash
# One-command deployment
./deploy.sh

# Or manually
docker build -t santander-api:latest .
docker run -d -p 8000:8000 --name santander-api santander-api:latest
```

### Step 4: Test API

```bash
# Run test client
python predict_client.py

# Or use curl
curl http://localhost:8000/health
```

**Access API Documentation:**
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## 📡 API Endpoints

### 1. `GET /` - Service Information

Returns basic API information and available endpoints.

**Response:**
```json
{
  "service": "Santander Product Recommendation Engine",
  "version": "1.0",
  "models_loaded": 21,
  "products": 24
}
```

### 2. `GET /health` - Health Check

Checks service status and model loading status.

**Response:**
```json
{
  "status": "ok",
  "models_loaded": 21,
  "products": 24
}
```

### 3. `POST /recommend` - Product Recommendation

Recommends top K products for a customer based on their features.

**Request:**
```json
{
  "customer_id": 12345,
  "features": {
    "age": 35,
    "renta": 100000.0,
    "antiguedad": 120,
    "month": 5,
    "segmento": 1
  },
  "owned_products": ["ind_cco_fin_ult1"],
  "k": 7,
  "return_scores": true
}
```

**Response:**
```json
{
  "customer_id": 12345,
  "recommendations": [
    "ind_cder_fin_ult1",
    "ind_ctju_fin_ult1",
    "ind_recibo_ult1",
    "ind_ecue_fin_ult1",
    "ind_nom_pens_ult1",
    "ind_reca_fin_ult1",
    "ind_nomina_ult1"
  ],
  "scores": {
    "ind_cder_fin_ult1": 1.0,
    "ind_ctju_fin_ult1": 0.153,
    "ind_recibo_ult1": 0.074
  }
}
```

### 4. `POST /explain` - Feature Importance Explanation

Explains why a specific product was recommended using feature importance values.

**Request:**
```json
{
  "customer_id": 12345,
  "features": {
    "age": 35,
    "renta": 100000.0,
    "antiguedad": 120,
    "month": 5
  },
  "product": "ind_cco_fin_ult1"
}
```

**Response:**
```json
{
  "customer_id": 12345,
  "product": "ind_cco_fin_ult1",
  "prediction_score": 0.559,
  "top_features": {
    "rel_month": -0.236,
    "prev_products_code_bucket": -0.095,
    "antiguedad": 0.041,
    "pop_prior_ind_ahor_fin_ult1": -0.031
  },
  "base_value": 0.1,
  "explanation": "Feature importance based on LightGBM gain. Positive values increase prediction, negative values decrease it."
}
```

### 5. `POST /fairness` - Fairness Evaluation

Evaluates recommendation fairness across demographic groups.

**Request:**
```json
{
  "customer_features_list": [
    {"age": 25, "renta": 50000, "antiguedad": 60, "month": 5, "segmento": 1},
    {"age": 45, "renta": 100000, "antiguedad": 120, "month": 5, "segmento": 2},
    {"age": 65, "renta": 70000, "antiguedad": 180, "month": 5, "segmento": 3}
  ],
  "demographic_attribute": "age",
  "k": 7
}
```

**Response:**
```json
{
  "demographic_attribute": "age",
  "groups": {
    "25.0": {"mean_score": 0.138, "std_score": 0.024, "count": 2},
    "45.0": {"mean_score": 0.342, "std_score": 0.079, "count": 2},
    "65.0": {"mean_score": 0.382, "std_score": 0.002, "count": 2}
  },
  "fairness_ratio": 2.77,
  "note": "Fairness ratio closer to 1.0 indicates more equal treatment across groups"
}
```

---

## 🏛️ Technical Architecture

### Model Architecture

- **Algorithm**: LightGBM (Gradient Boosting Decision Trees)
- **Task**: 21 independent binary classification models (one per product)
- **Hybrid Strategy**: Model predictions + popularity priors (alpha=0.5)
- **Features**: Customer demographics, product history, temporal features (~193 features)

### Recommendation Flow

```
Customer Features → Feature Engineering → 21 LightGBM Models
                                              ↓
                               Product Probability Scores
                                              ↓
                            Filter Owned Products
                                              ↓
                          Rank & Select Top K
                                              ↓
                              Return Recommendations
```

### Interpretability

- Uses LightGBM's native feature importance (gain-based)
- Provides top 10 most important features for each prediction
- Shows directional impact (positive/negative) on prediction
- Supports per-customer, per-product explanation

### Fairness Testing

- Evaluates recommendations across demographic groups (age, gender, income)
- Calculates mean AP@7 and standard deviation for each group
- Computes fairness ratio (max/min group performance)
- Identifies potential bias in recommendations

---

## 🌐 Cloud Deployment

### AWS ECS/Fargate

```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

aws ecr create-repository --repository-name santander-api

docker tag santander-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/santander-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/santander-api:latest

# Create ECS task definition and service (via AWS Console or CLI)
```

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/santander-api

gcloud run deploy santander-api \
  --image gcr.io/<project-id>/santander-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

### Azure Container Instances

```bash
# Create container registry
az acr create --resource-group santander-rg \
  --name santanderregistry --sku Basic

# Build and push
az acr build --registry santanderregistry \
  --image santander-api:latest .

# Deploy
az container create \
  --resource-group santander-rg \
  --name santander-api \
  --image santanderregistry.azurecr.io/santander-api:latest \
  --dns-name-label santander-api \
  --ports 8000 \
  --cpu 2 \
  --memory 4
```

---

## ⚡ Performance Optimization

1. **Model Loading**: Pre-load models at startup (already implemented)
2. **Batch Inference**: Support batch customer recommendations
3. **Feature Caching**: Cache common feature computations
4. **Horizontal Scaling**: Increase uvicorn workers or deploy multiple container instances
5. **GPU Acceleration**: Consider GPU for large-scale inference (requires LightGBM GPU version)

**Scaling Example:**
```bash
# Increase workers for better throughput
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4

# Or use gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 📈 Monitoring & Logging

**Recommended Tools:**
- **Prometheus**: Metrics collection (request latency, throughput, error rate)
- **Grafana**: Visualization dashboards
- **ELK Stack**: Centralized logging (Elasticsearch + Logstash + Kibana)
- **Sentry**: Error tracking and alerting

**Key Metrics to Track:**
- Request latency (p50, p95, p99)
- Requests per second
- Model inference time
- Error rate
- Recommendation distribution
- Fairness metrics over time

---

## 📊 Performance Benchmarks

| Metric | Value |
|--------|-------|
| **MAP@7** (model only) | 0.0141 |
| **MAP@7** (hybrid) | 0.0147 |
| **Average AUC** | 0.85 |
| **Training Data** | 10M+ records (18 months) |
| **Features** | 193 engineered features |
| **Products** | 21 trained models (24 total) |
| **Inference Latency** | <100ms per customer (single core) |
| **Model Size** | ~50MB (all 21 models) |

---

## 🛠️ Development

### Running Tests

```bash
# Test all endpoints
python predict_client.py

# Test individual endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/recommend -H "Content-Type: application/json" -d @sample_request.json
```

### Managing API Service

```bash
# Check if API is running
lsof -i :8000

# Stop API
pkill -f "uvicorn app:app"

# Restart API
./deploy.sh --local

# View logs
tail -f api.log
```

### Updating Models

1. Re-run the training notebook with new data
2. New models will be saved to `models/` directory
3. Restart the API service to load updated models

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)**: Beginner-friendly quick start guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Comprehensive deployment instructions
- **[MODEL_IMPROVEMENTS.md](MODEL_IMPROVEMENTS.md)**: Performance optimization guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**: Detailed project overview

---

## 🎯 Resume Highlights

This project demonstrates:

✅ **Large-Scale ML System**: Built recommendation engine processing 10M+ records  
✅ **Production Deployment**: End-to-end ML workflow from data to Docker deployment  
✅ **Model Interpretability**: Implemented feature importance analysis for explainability  
✅ **Fairness & Ethics**: Evaluated and addressed demographic bias in recommendations  
✅ **Software Engineering**: RESTful API, containerization, automated deployment  
✅ **Performance Optimization**: Achieved competitive MAP@7 score with hybrid approach

---

## 📄 Data Source

- **Dataset**: [Santander Product Recommendation (Kaggle)](https://www.kaggle.com/c/santander-product-recommendation)
- **Training Data**: January 2015 - April 2016 (16 months)
- **Validation Data**: May 2016
- **Test Data**: June 2016
- **Records**: 10M+ customer transactions
- **Products**: 24 financial products

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Yiru Chen**  
Data Scientist / ML Engineer

---

## 🙏 Acknowledgments

- Santander Bank for providing the dataset
- Kaggle community for insights and discussions
- LightGBM developers for the excellent library
- FastAPI team for the modern web framework

---

## 📞 Contact & Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check the [documentation](DEPLOYMENT.md)
- Review the [FAQ](QUICK_START.md)

---

**Built with ❤️ using Python, LightGBM, and FastAPI**
