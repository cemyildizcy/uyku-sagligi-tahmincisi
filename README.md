# 🌙 Sleep Health Predictor — AI-Powered Sleep Disorder Risk Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit)](https://streamlit.io)
[![XGBoost](https://img.shields.io/badge/XGBoost-95%25%20Accuracy-green)](https://xgboost.readthedocs.io)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3FCF8E?logo=supabase)](https://supabase.com)
[![Gemini AI](https://img.shields.io/badge/AI%20Coach-Google%20Gemini-4285F4?logo=google)](https://ai.google.dev)

> An end-to-end machine learning web application that predicts sleep disorder risk from user health and lifestyle metrics. Built with a model competition pipeline, real-time AI coaching, and a cloud-backed user profile system.

---

## 🎯 Project Overview

This project was developed to demonstrate a complete **Data Science and MLOps pipeline** — from raw data analysis and model training to a production-ready, deployed web application.

The application collects 13 key health and lifestyle metrics from the user and uses a trained **XGBoost classifier** (**95.3% cross-validated accuracy**) to assess their sleep disorder risk as `Healthy`, `Mild Risk`, or `High Risk`. After the prediction, a **Google Gemini 2.5** AI model generates a personalized, expert-level sleep coaching comment in real-time.

---

## 🚀 Live Demo

> 🔗 **[sleep-health-predictor.streamlit.app](https://share.streamlit.io)** *(Deployment Link)*

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **🤖 Model Competition** | Random Forest, Gradient Boosting & XGBoost trained and compared via 5-Fold CV |
| **📊 Feature Selection** | Importance analysis run to remove 16 low-impact/leakage features from 29 total |
| **🔒 Data Leakage Prevention** | Outcome proxies (`sleep_quality_score`) deliberately excluded from training |
| **👤 User Authentication** | Secure Register/Login system with `bcrypt`-hashed passwords |
| **☁️ Cloud Database** | User profiles persisted to Supabase PostgreSQL (survives server resets) |
| **🧠 AI Sleep Coach** | Google Gemini 2.5 Flash generates personalized Turkish-language sleep advice |
| **💾 Profile System** | Save & load personal metric profiles per authenticated account |

---

## 🛠️ Technical Stack

**Machine Learning & Data Science**
- `scikit-learn` — Preprocessing, model evaluation (Cross-Validation, Label Encoding, Standard Scaling)
- `XGBoost` — Primary classifier (winner of 3-model competition)
- `pandas` / `numpy` — Data manipulation and analysis
- `joblib` — Model artifact serialization

**Web Application & Infrastructure**
- `Streamlit` — Interactive web UI
- `Supabase` — Cloud PostgreSQL database (via REST API)
- `Google Generative AI` — Gemini 2.5 Flash for personalized AI coaching
- `bcrypt` — Secure password hashing
- `Plotly` — Interactive data comparison charts

---

## 📊 Model Development Pipeline

```
100,000-row Dataset
        │
        ▼
Feature Analysis (29 features)
        │
        ▼
Importance Ranking → Removed 16 low-impact features
        │
        ▼
Leakage Detection → Removed outcome-proxies (e.g., sleep_quality_score)
        │
        ▼
3-Model Competition (5-Fold Cross Validation)
├── Random Forest:        93.6% CV Accuracy
├── Gradient Boosting:    92.4% CV Accuracy
└── XGBoost:         ✅  95.3% CV Accuracy  ← WINNER
        │
        ▼
Final Model Trained on 80,000 rows → Tested on 20,000 rows
Final Test Accuracy: 95.29%
```

---

## 📁 Project Structure

```
sleep-health-predictor/
│
├── app.py                  # Streamlit UI — Auth, Forms, Prediction, AI Coach
├── train_model.py          # ML pipeline — Training, CV, Artifact export
├── requirements.txt        # Python dependencies
├── .gitignore              # Protects API keys from being committed
│
├── models/                 # Trained model artifacts (auto-generated)
│   ├── best_model.joblib
│   ├── scaler.joblib
│   ├── label_encoders.joblib
│   ├── target_le.joblib
│   ├── feature_defaults.joblib
│   ├── expected_features.joblib
│   └── feature_uniques.joblib
│
└── .streamlit/
    └── secrets.toml        # API keys (NOT committed to GitHub)
```

---

## ⚙️ Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/sleep-health-predictor.git
cd sleep-health-predictor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train the model (requires sleep_health_dataset.csv in root)
python train_model.py

# 4. Create secrets file
mkdir .streamlit
# Add your keys to .streamlit/secrets.toml (see secrets format below)

# 5. Run the app
streamlit run app.py
```

**`.streamlit/secrets.toml` format:**
```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "your_supabase_key"
GEMINI_API_KEY = "your_gemini_key"
```

---

## 🔬 Key Design Decisions

1. **Preventing Data Leakage:** Features like `sleep_quality_score` and `cognitive_performance_score` were deliberately excluded. Despite being top-2 in importance rankings, they are outcome proxies — including them would give the model a "cheat sheet" and make it trivially easy but practically useless.

2. **Feature Engineering:** After importance analysis, 16 features with <1% impact (room temperature, season, day type, etc.) were pruned. The final 13-feature set achieves the same 95.3% accuracy as the full 29-feature model.

3. **Cloud-first Architecture:** Using Supabase instead of local JSON files ensures user data persists across server restarts on free-tier hosting — a critical production consideration.

---

## 📈 Results

| Metric | Value |
|---|---|
| Training Dataset Size | 100,000 rows |
| Features Used | 13 (selected from 29) |
| CV Folds | 5-Fold Stratified |
| Best Model | XGBoost |
| Cross-Val Accuracy | **95.30%** |
| Test Set Accuracy | **95.29%** |

---

## 👤 Author

**Cem Yıldız**
*Data Science & Machine Learning Portfolio Project*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com)
