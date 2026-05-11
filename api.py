import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import pandas as pd
import joblib
import bcrypt
from supabase import create_client, Client
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Supabase & Gemini Setup ---
try:
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)

    gemini_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=gemini_key)
    model_ai = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error setting up clients: {e}")

# --- Load Models ---
model_dir = "models"
try:
    ml_model = joblib.load(os.path.join(model_dir, "best_model.joblib"))
    scaler = joblib.load(os.path.join(model_dir, "scaler.joblib"))
    label_encoders = joblib.load(os.path.join(model_dir, "label_encoders.joblib"))
    target_le = joblib.load(os.path.join(model_dir, "target_le.joblib"))
    feature_defaults = joblib.load(os.path.join(model_dir, "feature_defaults.joblib"))
    expected_features = joblib.load(os.path.join(model_dir, "expected_features.joblib"))
except Exception as e:
    print(f"Error loading models: {e}")

# --- Pydantic Models ---
class UserAuth(BaseModel):
    email: str
    password: str

class ProfileSave(BaseModel):
    email: str
    profile_name: str
    profile_data: Dict[str, Any]

class PredictionRequest(BaseModel):
    inputs: Dict[str, Any]
    email: Optional[str] = None
    profile_name: Optional[str] = None

# --- Database Helpers ---
def get_user(email: str):
    response = supabase.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_profile_history(email: str, profile_name: str, limit: int = 30):
    """Belirli bir profilin son N analiz kaydını getir."""
    try:
        response = (
            supabase.table("analysis_logs")
            .select("*")
            .eq("email", email)
            .eq("profile_name", profile_name)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"History fetch error: {e}")
        return []

def save_analysis_log(email: str, profile_name: str, inputs: dict, risk_label: str, translated_risk: str, probability: float):
    """Analiz sonucunu loglara kaydet."""
    try:
        supabase.table("analysis_logs").insert({
            "email": email,
            "profile_name": profile_name,
            "inputs": inputs,
            "risk_label": risk_label,
            "translated_risk": translated_risk,
            "probability": probability,
        }).execute()
    except Exception as e:
        print(f"Log save error: {e}")

# --- Endpoints ---

@app.get("/")
def health_check():
    """Uptime robotları için uyku engelleyici endpoint"""
    return {"status": "awake", "message": "SleepInfo API is running."}

@app.post("/api/auth/register")
def register(user: UserAuth):
    existing_user = get_user(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    hashed = hash_password(user.password)
    response = supabase.table("users").insert({"email": user.email, "password_hash": hashed, "profiles": {}}).execute()
    return {"message": "Registration successful"}

@app.post("/api/auth/login")
def login(user: UserAuth):
    existing_user = get_user(user.email)
    if not existing_user:
        raise HTTPException(status_code=400, detail="User not found")
    if not check_password(user.password, existing_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    return {"email": existing_user["email"], "profiles": existing_user.get("profiles", {})}

@app.get("/api/profiles/{email}")
def get_profiles(email: str):
    user = get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"profiles": user.get("profiles", {})}

@app.post("/api/profiles")
def save_profile(data: ProfileSave):
    user = get_user(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profiles = user.get("profiles", {})
    profiles[data.profile_name] = data.profile_data
    
    supabase.table("users").update({"profiles": profiles}).eq("email", data.email).execute()
    return {"message": "Profile saved successfully", "profiles": profiles}

@app.delete("/api/profiles/{email}/{profile_name}")
def delete_profile(email: str, profile_name: str):
    user = get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profiles = user.get("profiles", {})
    if profile_name in profiles:
        del profiles[profile_name]
        supabase.table("users").update({"profiles": profiles}).eq("email", email).execute()
    return {"message": "Profile deleted", "profiles": profiles}

# --- History Endpoint ---
@app.get("/api/history/{email}/{profile_name}")
def get_history(email: str, profile_name: str):
    """Belirli bir profilin son 30 analiz kaydını döndürür."""
    history = get_profile_history(email, profile_name, limit=30)
    return {"history": history}

@app.delete("/api/history/{log_id}")
def delete_history_log(log_id: int):
    """Belirli bir geçmiş log kaydını siler."""
    try:
        supabase.table("analysis_logs").delete().eq("id", log_id).execute()
        return {"message": "Log deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Prediction ---
@app.post("/api/predict")
def predict(request: PredictionRequest):
    user_inputs = request.inputs
    email = request.email
    profile_name = request.profile_name or "default"
    
    try:
        # Check for missing expected features and fill with defaults
        for f in expected_features:
            if f not in user_inputs or user_inputs[f] is None:
                user_inputs[f] = feature_defaults.get(f)

        input_df = pd.DataFrame([user_inputs])
        
        # Ensure columns match the exact order expected by the model
        input_df = input_df[expected_features]

        # 1. Encoding
        for col in label_encoders:
            if col in input_df.columns:
                le = label_encoders[col]
                val = input_df[col].iloc[0]
                if val in le.classes_:
                    input_df[col] = le.transform([val])
                else:
                    input_df[col] = le.transform([le.classes_[0]])

        # 2. Scaling
        categorical_cols = list(label_encoders.keys())
        numerical_cols = [col for col in expected_features if col not in categorical_cols]
        input_df[numerical_cols] = scaler.transform(input_df[numerical_cols])

        # 3. Predict
        pred_encoded = ml_model.predict(input_df)[0]
        pred_proba = ml_model.predict_proba(input_df)[0]
        risk_label = target_le.inverse_transform([pred_encoded])[0]
        
        risk_translation = {
            "Healthy": "Sağlıklı",
            "Mild": "Hafif Risk",
            "Moderate": "Orta Risk",
            "Severe": "Yüksek Risk",
            "None": "Sağlıklı"
        }
        translated_risk = risk_translation.get(risk_label, risk_label)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")

    # 4. Save analysis log
    if email:
        save_analysis_log(
            email=email,
            profile_name=profile_name,
            inputs={k: float(v) if isinstance(v, (int, float)) else str(v) for k, v in user_inputs.items()},
            risk_label=str(risk_label),
            translated_risk=str(translated_risk),
            probability=float(max(pred_proba))
        )

    # 5. Get history for AI context
    history_summary = ""
    history_data = []
    if email:
        history_data = get_profile_history(email, profile_name, limit=5)
        if history_data:
            history_lines = []
            for i, h in enumerate(history_data):
                ts = h.get("created_at", "")[:10]
                history_lines.append(
                    f"  - {ts}: Sonuç={h.get('translated_risk')}, "
                    f"Uyku={h.get('inputs', {}).get('sleep_duration_hrs', '?')}s, "
                    f"Stres={h.get('inputs', {}).get('stress_score', '?')}, "
                    f"Kafein={h.get('inputs', {}).get('caffeine_mg_before_bed', '?')}mg"
                )
            history_summary = f"""
        
        Bu hastanın geçmiş analiz kayıtları (en yeniden eskiye, profil: {profile_name}):
{chr(10).join(history_lines)}
        
        Lütfen geçmiş verilerle kıyaslama yaparak gelişimi hakkında yorum yap. 
        İyileşme varsa tebrik et, kötüleşme varsa nazikçe uyar ve somut öneriler ver.
        Eğer bu ilk analiz ise, düzenli takip yapmasını öner.
        """

    # 6. Gemini AI Coach
    ai_feedback = ""
    try:
        prompt = f"""
        Sen profesyonel, şefkatli ve bilimsel konuşan bir uyku doktorusun. 
        Sistemimiz bir hasta için '{translated_risk}' sonucunu buldu. 
        Hastanın bazı temel bilgileri: 
        - Yaş: {user_inputs.get('age')}
        - Uyku süresi: {user_inputs.get('sleep_duration_hrs')} saat
        - Günlük Stres (0-10): {user_inputs.get('stress_score')}
        - Kafein tüketimi: {user_inputs.get('caffeine_mg_before_bed')} mg
        - Alkol tüketimi: {user_inputs.get('alcohol_units_before_bed')} birim
        - BMI (Vücut Kitle İndeksi): {user_inputs.get('bmi')}
        {history_summary}
        Lütfen bu hastaya doğrudan hitap ederek ("Merhaba, verilerinizi inceledim..." gibi), 
        uyku kalitesini artırması veya mevcut durumunu koruması için Türkçe, samimi ve motive edici 2-3 paragraflık bir değerlendirme ve tavsiye yazısı oluştur.
        Maddeler kullanabilirsin. Sonucu çok uzun tutma.
        """
        response = model_ai.generate_content(prompt)
        try:
            ai_feedback = response.text
        except ValueError:
            ai_feedback = "Yapay zeka analizimizi üretti, ancak Google güvenlik politikalarına takıldığı için metni gösteremiyoruz."
    except Exception as e:
        print(f"AI Error: {e}")
        ai_feedback = f"Yapay zeka ile iletişim kurulamadı. Lütfen API anahtarınızı veya model sürümünü kontrol edin. (Hata: {str(e)[:50]})"

    # Return structured data
    max_prob = float(max(pred_proba))
    return {
        "risk_label": str(risk_label),
        "translated_risk": str(translated_risk),
        "probability": max_prob,
        "ai_feedback": ai_feedback,
        "chart_data": {
            "user_values": {
                "Gece Uyanma Sayısı": float(user_inputs.get("wake_episodes_per_night", 0)),
                "Uyku Süresi (Saat)": float(user_inputs.get("sleep_duration_hrs", 0)),
                "Kafein (mg)": float(user_inputs.get("caffeine_mg_before_bed", 0)),
                "Uykuya Dalma Süresi": float(user_inputs.get("sleep_latency_mins", 0)),
                "Stres Skoru": float(user_inputs.get("stress_score", 0))
            },
            "average_values": {
                "Gece Uyanma Sayısı": float(feature_defaults.get("wake_episodes_per_night", 0)),
                "Uyku Süresi (Saat)": float(feature_defaults.get("sleep_duration_hrs", 0)),
                "Kafein (mg)": float(feature_defaults.get("caffeine_mg_before_bed", 0)),
                "Uykuya Dalma Süresi": float(feature_defaults.get("sleep_latency_mins", 0)),
                "Stres Skoru": float(feature_defaults.get("stress_score", 0))
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
