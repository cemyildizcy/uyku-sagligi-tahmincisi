import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
import joblib
import os

def main():
    data_path = "sleep_health_dataset.csv"
    
    if not os.path.exists(data_path):
        print(f"Hata: {data_path} bulunamadı!")
        return

    print("Veri yükleniyor...")
    df = pd.read_csv(data_path)

    # Sadece en önemli ve mantıklı 13 özelliği (kopya çekenleri çıkararak) seçiyoruz.
    selected_features = [
        "mental_health_condition", "bmi", "wake_episodes_per_night", 
        "sleep_duration_hrs", "sleep_latency_mins", "shift_work", 
        "stress_score", "alcohol_units_before_bed", "exercise_day", 
        "caffeine_mg_before_bed", "age", "felt_rested", "rem_percentage"
    ]

    # Hedef ve özellik ayırma
    target_col = "sleep_disorder_risk"
    y = df[target_col]
    X = df[selected_features]

    # Kategorik sütunlar (sadece mental_health_condition kaldı, diğerleri elendi)
    categorical_cols = ["mental_health_condition"]
    
    # Beklenen özellikleri sıralı tutalım
    expected_features = list(X.columns)

    print("Eksik değerler işleniyor ve varsayılanlar hesaplanıyor...")
    for col in X.columns:
        if X[col].dtype == "object":
            X[col] = X[col].fillna(X[col].mode()[0])
        else:
            X[col] = X[col].fillna(X[col].mean())

    y = y.fillna(y.mode()[0])

    feature_defaults = {}
    feature_uniques = {}
    for col in X.columns:
        if col in categorical_cols:
            feature_defaults[col] = X[col].mode()[0]
            feature_uniques[col] = X[col].unique().tolist()
        else:
            feature_defaults[col] = float(X[col].mean())
            feature_uniques[col] = None

    print("Kategorik veriler dönüştürülüyor...")
    label_encoders = {}
    for col in categorical_cols:
        if col in X.columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            label_encoders[col] = le

    target_le = LabelEncoder()
    y_encoded = target_le.fit_transform(y.astype(str))

    print("Veriler ölçeklendiriliyor...")
    scaler = StandardScaler()
    numerical_cols = [col for col in X.columns if col not in categorical_cols]
    X[numerical_cols] = scaler.fit_transform(X[numerical_cols])

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    print("Model Yarışması Başlıyor (5-Fold Cross Validation)...")
    
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42, n_jobs=-1)
    }

    best_model_name = ""
    best_model = None
    best_score = 0

    for name, model in models.items():
        # CV Score
        scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy', n_jobs=-1)
        mean_score = scores.mean()
        print(f"{name} CV Ortalama Doğruluğu: {mean_score:.4f} (+/- {scores.std():.4f})")
        
        if mean_score > best_score:
            best_score = mean_score
            best_model_name = name
            best_model = model

    print(f"\nKazanan Model: {best_model_name} (CV Doğruluğu: {best_score:.4f})")
    
    print(f"{best_model_name} tüm eğitim verisiyle eğitiliyor...")
    best_model.fit(X_train, y_train)
    
    test_acc = best_model.score(X_test, y_test)
    print(f"Test Verisi Üzerindeki Başarısı: {test_acc:.4f}")

    print("Model ve nesneler kaydediliyor...")
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model, "models/best_model.joblib")
    joblib.dump(scaler, "models/scaler.joblib")
    joblib.dump(label_encoders, "models/label_encoders.joblib")
    joblib.dump(target_le, "models/target_le.joblib")
    joblib.dump(feature_defaults, "models/feature_defaults.joblib")
    joblib.dump(expected_features, "models/expected_features.joblib")
    joblib.dump(feature_uniques, "models/feature_uniques.joblib")

    print("Tüm işlemler başarıyla tamamlandı. Yeni model 'models/best_model.joblib' olarak kaydedildi.")

if __name__ == "__main__":
    main()
