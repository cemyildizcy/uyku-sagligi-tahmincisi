import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as plotly_express
import os
import bcrypt
from supabase import create_client, Client
import google.generativeai as genai

# --- Page Config ---
st.set_page_config(page_title="Uyku Sağlığı Tahmincisi", page_icon="🌙", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { color: #e0e0e0; }
    .card {
        background: rgba(30, 30, 40, 0.7);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .title-text {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3em;
        margin-bottom: 5px;
    }
    .subtitle-text {
        text-align: center;
        color: #a0a0b0;
        margin-bottom: 30px;
    }
    .result-card-healthy {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white; border-radius: 15px; padding: 25px; text-align: center;
        box-shadow: 0 10px 20px rgba(56, 239, 125, 0.3);
    }
    .result-card-risk {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white; border-radius: 15px; padding: 25px; text-align: center;
        box-shadow: 0 10px 20px rgba(255, 65, 108, 0.3);
    }
    .result-card-mild {
        background: linear-gradient(135deg, #f7b733 0%, #fc4a1a 100%);
        color: white; border-radius: 15px; padding: 25px; text-align: center;
        box-shadow: 0 10px 20px rgba(247, 183, 51, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Supabase & Gemini Setup ---
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(supabase_url, supabase_key)
    
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
    model_ai = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"Sistem ayarları eksik! Lütfen .streamlit/secrets.toml dosyasını oluşturup SUPABASE ve GEMINI anahtarlarınızı girin. Hata: {e}")
    st.stop()

# --- Translation Maps ---
translation_map = {
    "gender": {"Kadın": "Female", "Erkek": "Male", "Diğer": "Other"},
    "occupation": {"Sürücü": "Driver", "Yazılım Mühendisi": "Software Engineer", "Hemşire": "Nurse", "Öğrenci": "Student", "Avukat": "Lawyer", "Serbest Çalışan": "Freelancer", "Yönetici": "Manager", "Doktor": "Doctor", "Ev Hanımı": "Homemaker", "Öğretmen": "Teacher", "Emekli": "Retired", "Satış": "Sales"},
    "chronotype": {"Sabahçıl": "Morning", "Nötr": "Neutral", "Akşamcıl": "Evening"},
    "mental_health_condition": {"Sağlıklı": "Healthy", "Anksiyete ve Depresyon": "Both", "Depresyon": "Depression", "Anksiyete": "Anxiety"},
    "season": {"Sonbahar": "Autumn", "Kış": "Winter", "İlkbahar": "Spring", "Yaz": "Summer"},
    "day_type": {"Hafta İçi": "Weekday", "Hafta Sonu": "Weekend"}
}

# --- Load Models ---
@st.cache_resource
def load_models():
    model_dir = "models"
    try:
        model = joblib.load(os.path.join(model_dir, "best_model.joblib"))
        scaler = joblib.load(os.path.join(model_dir, "scaler.joblib"))
        label_encoders = joblib.load(os.path.join(model_dir, "label_encoders.joblib"))
        target_le = joblib.load(os.path.join(model_dir, "target_le.joblib"))
        feature_defaults = joblib.load(os.path.join(model_dir, "feature_defaults.joblib"))
        expected_features = joblib.load(os.path.join(model_dir, "expected_features.joblib"))
        feature_uniques = joblib.load(os.path.join(model_dir, "feature_uniques.joblib"))
        return model, scaler, label_encoders, target_le, feature_defaults, expected_features, feature_uniques
    except Exception as e:
        st.error(f"Model dosyaları yüklenemedi. Lütfen önce train_model.py çalıştırın. Hata: {e}")
        return None, None, None, None, None, None, None

model, scaler, label_encoders, target_le, feature_defaults, expected_features, feature_uniques = load_models()

if model is None:
    st.stop()

# --- Database Management (Supabase) ---
def get_user(email):
    response = supabase.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None

def create_user(email, password_hash):
    supabase.table("users").insert({"email": email, "password_hash": password_hash, "profiles": {}}).execute()

def update_profiles(email, profiles):
    supabase.table("users").update({"profiles": profiles}).eq("email", email).execute()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# --- Session State Init ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# --- AUTHENTICATION UI ---
if not st.session_state["logged_in"]:
    st.markdown("<h1 class='title-text'>🌙 Uyku Sağlığı Tahmincisi</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>Kişisel verilerinizi korumak için lütfen giriş yapın.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        auth_tab1, auth_tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
        
        with auth_tab1:
            st.subheader("Giriş Yap")
            login_email = st.text_input("E-posta Adresi", key="login_email")
            login_password = st.text_input("Şifre", type="password", key="login_pass")
            if st.button("Giriş", use_container_width=True):
                user_data = get_user(login_email)
                if user_data:
                    if check_password(login_password, user_data["password_hash"]):
                        st.session_state["logged_in"] = True
                        st.session_state["user_email"] = login_email
                        st.rerun()
                    else:
                        st.error("Hatalı şifre!")
                else:
                    st.error("Kullanıcı bulunamadı!")
            
            st.markdown("---")
            st.button("🌐 Google ile Giriş Yap (Çok Yakında)", disabled=True, use_container_width=True)
                    
        with auth_tab2:
            st.subheader("Yeni Hesap Oluştur")
            reg_email = st.text_input("E-posta Adresi", key="reg_email")
            reg_password = st.text_input("Şifre", type="password", key="reg_pass")
            reg_password_confirm = st.text_input("Şifreyi Onayla", type="password", key="reg_pass2")
            if st.button("Kayıt Ol", use_container_width=True):
                user_data = get_user(reg_email)
                if user_data:
                    st.error("Bu e-posta adresi zaten kayıtlı!")
                elif reg_password != reg_password_confirm:
                    st.error("Şifreler uyuşmuyor!")
                elif len(reg_password) < 6:
                    st.error("Şifre en az 6 karakter olmalıdır.")
                elif not reg_email or "@" not in reg_email:
                    st.error("Lütfen geçerli bir e-posta girin.")
                else:
                    create_user(reg_email, hash_password(reg_password))
                    st.success("Kayıt başarılı! Giriş sekmesinden giriş yapabilirsiniz.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.stop()


# --- MAIN APP (LOGGED IN) ---
current_user = get_user(st.session_state["user_email"])
user_profiles = current_user.get("profiles", {}) if current_user else {}

st.sidebar.markdown(f"**Hesap:** `{st.session_state['user_email']}`")
if st.sidebar.button("🚪 Çıkış Yap"):
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Profil Yönetimi")
profile_names = list(user_profiles.keys())

selected_profile = st.sidebar.selectbox("Kayıtlı Profil Seçin", ["-- Yeni Seçim (Boş) --"] + profile_names)

if st.sidebar.button("🔄 Profili Yükle") and selected_profile != "-- Yeni Seçim (Boş) --":
    prof_data = user_profiles[selected_profile]
    for k, v in prof_data.items():
        st.session_state[k] = v
    st.sidebar.success(f"'{selected_profile}' başarıyla yüklendi!")

st.sidebar.markdown("---")
new_profile_name = st.sidebar.text_input("Profili Kaydetmek İçin İsim Girin:")
if st.sidebar.button("💾 Mevcut Girdileri Buluta Kaydet"):
    if new_profile_name:
        current_inputs = {}
        for col in expected_features:
            val = st.session_state.get(col)
            current_inputs[col] = val
        
        user_profiles[new_profile_name] = current_inputs
        update_profiles(st.session_state["user_email"], user_profiles)
        st.sidebar.success(f"'{new_profile_name}' profiliniz Supabase bulutuna kaydedildi!")
    else:
        st.sidebar.error("Lütfen bir profil adı girin.")


st.markdown("<h1 class='title-text'>🌙 Uyku Sağlığı Tahmincisi</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Yapay zeka tüm detayları analiz ederek uyku riskinizi hesaplar.</p>", unsafe_allow_html=True)

# --- Tooltips / Yardım Metinleri ---
feature_hints = {
    "age": "Kişinin yaşı (Örn: 25, 40).",
    "gender": "Biyolojik cinsiyetiniz. Cinsiyetin uyku düzeni üzerindeki istatistiksel etkileri için kullanılır.",
    "occupation": "Genel meslek grubunuz veya gün içindeki ana uğraşınız.",
    "bmi": "Vücut Kitle İndeksi (Kilo / Boy²). Örn: Normal kilolu biri için 22-25 arasıdır.",
    "season": "Testi yaptığınız veya değerleri girdiğiniz güncel mevsim.",
    "day_type": "Girdiğiniz veriler genellikle hafta içi mi yoksa hafta sonu alışkanlıklarınız mı?",
    "work_hours_that_day": "Günde ortalama kaç saat çalışıyorsunuz veya ders çalışıyorsunuz? (Örn: 8.5)",
    "screen_time_before_bed_mins": "Uyumadan hemen önce telefona veya ekrana kaç dakika bakıyorsunuz? (Örn: 45)",
    "caffeine_mg_before_bed": "Uyumadan önceki saatlerde alınan kafein miktarı (1 Fincan Türk Kahvesi = ~60mg, 1 Kupa Filtre = ~100mg, Çay = ~40mg).",
    "alcohol_units_before_bed": "Uyumadan önce alınan alkol birimi. Kullanmıyorsanız 0 yazın.",
    "steps_that_day": "Günlük ortalama adım sayınız. Akıllı saat veya telefondan ortalamanıza bakabilirsiniz (Örn: 5000, 10000).",
    "exercise_day": "Genel günlerde en az 30 dk düzenli egzersiz yapıyor musunuz?",
    "stress_score": "Genel stres seviyeniz. 0: Hiç stresli değilim, 10: Çok fazla stresliyim.",
    "mental_health_condition": "Tanısı konulmuş veya kendinizde hissettiğiniz ruh sağlığı durumu.",
    "chronotype": "Uyku tercihiniz. Sabah erken kalkmayı seviyorsanız Sabahçıl, gece oturmayı seviyorsanız Akşamcıl.",
    "shift_work": "Gündüz/Gece dönüşümlü vardiyalı bir işte çalışıyor musunuz?",
    "cognitive_performance_score": "Gün içi odaklanma ve zihinsel zindelik skorunuz (0-100). Gün boyu odaklanma sorunu yaşıyorsanız 30-50, zihninizi çok berrak hissediyorsanız 80-100 arası yazın.",
    "sleep_duration_hrs": "Geceleri ortalama ne kadar uyuyorsunuz? (Örn: 7.5)",
    "sleep_quality_score": "Kendi hissinize göre uykunuzun kalitesi (0-10). 10 harika, 0 berbat demektir. Genelde 6-8 arası normal kabul edilir.",
    "rem_percentage": "Uykunuzun yüzde kaçını REM (Rüya) evresinde geçiriyorsunuz? Akıllı saatiniz yoksa tahmini %20-25 arası girebilirsiniz.",
    "deep_sleep_percentage": "Uykunuzun yüzde kaçını Derin Uyku evresinde geçiriyorsunuz? Akıllı saatiniz yoksa tahmini %15-20 arası girebilirsiniz.",
    "sleep_latency_mins": "Yatağa yattıktan sonra uykuya dalmanız ortalama kaç dakika sürüyor?",
    "wake_episodes_per_night": "Gece boyunca uykunuz ortalama kaç kez bölünüyor?",
    "nap_duration_mins": "Gündüzleri ortalama kaç dakika şekerleme (kısa uyku) yapıyorsunuz? Yapmıyorsanız 0 yazın.",
    "heart_rate_resting_bpm": "Dinlenik Kalp Atış Hızınız (Nabız). Bilmiyorsanız 60-70 arası standart bir değer girebilirsiniz.",
    "room_temperature_celsius": "Yattığınız odanın ortalama sıcaklığı (Derece). (Örn: 21, 22)",
    "weekend_sleep_diff_hrs": "Hafta içi ile hafta sonu uyku süreniz arasındaki fark. (Örn: Hafta sonu 2 saat fazla uyuyorsanız 2 yazın).",
    "sleep_aid_used": "Uykuya dalmak için hap, çay veya medikal destek alıyor musunuz?",
    "felt_rested": "Sabahları genellikle dinlenmiş ve enerjik uyanıyor musunuz?"
}

# Helper function to create inputs
def get_input(col, label):
    default_val = feature_defaults.get(col)
    uniques = feature_uniques.get(col)
    hint = feature_hints.get(col, "")
    
    if uniques is not None:
        # Kategorik
        eng_to_turk = {v: k for k, v in translation_map[col].items()}
        turkish_options = [eng_to_turk.get(u, u) for u in uniques]
        default_turk = eng_to_turk.get(default_val, default_val)
        
        return st.selectbox(label, options=turkish_options, index=None, placeholder=f"Örn: {default_turk}", help=hint, key=col)
    else:
        # Sayısal
        if default_val is not None:
            if isinstance(default_val, int) or default_val.is_integer():
                ph = f"Örn: {int(default_val)}"
                step = 1.0
            else:
                ph = f"Örn: {default_val:.2f}"
                step = 0.1
            
            return st.number_input(label, value=None, placeholder=ph, step=step, help=hint, key=col)
        else:
            return st.number_input(label, value=None, step=1.0, help=hint, key=col)

st.markdown("### 📋 Lütfen Bilgileri Eksiksiz Doldurun")

tab1, tab2, tab3 = st.tabs(["👤 Profil & Demografi", "🏃 Günlük Alışkanlıklar", "🛌 Uyku Metrikleri"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        get_input("age", "Yaş")
        get_input("bmi", "Vücut Kitle İndeksi (BMI)")
    with c2:
        get_input("mental_health_condition", "Ruh Sağlığı Durumu")
        get_input("shift_work", "Vardiyalı Çalışma Var mı? (0: Hayır, 1: Evet)")

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        get_input("caffeine_mg_before_bed", "Kafein Tüketimi (mg)")
        get_input("alcohol_units_before_bed", "Alkol Tüketimi (Birim)")
    with c2:
        get_input("exercise_day", "O Gün Egzersiz Yapıldı mı? (0: Hayır, 1: Evet)")
        get_input("stress_score", "Stres Skoru (0-10)")

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        get_input("sleep_duration_hrs", "Uyku Süresi (Saat)")
        get_input("rem_percentage", "REM Uyku Yüzdesi")
        get_input("felt_rested", "Dinlenmiş Hissediyor musunuz? (0: Hayır, 1: Evet)")
    with c2:
        get_input("sleep_latency_mins", "Uykuya Dalma Süresi (Dk)")
        get_input("wake_episodes_per_night", "Gece Uyanma Sayısı")


st.markdown("---")
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
predict_btn = st.button("🚀 Analizi Başlat", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if predict_btn:
    missing_fields = []
    user_inputs = {}
    
    for col in expected_features:
        val = st.session_state.get(col)
        if val is None:
            missing_fields.append(col)
        else:
            uniques = feature_uniques.get(col)
            if uniques is not None:
                turk_to_eng = translation_map[col]
                user_inputs[col] = turk_to_eng.get(val, val)
            else:
                user_inputs[col] = val

    if missing_fields:
        st.error("⚠️ Lütfen tüm alanları doldurun! Yukarıdaki alanlardan eksik bıraktıklarınız var.")
    else:
        input_df = pd.DataFrame([user_inputs])

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
        pred_encoded = model.predict(input_df)[0]
        pred_proba = model.predict_proba(input_df)[0]
        risk_label = target_le.inverse_transform([pred_encoded])[0]

        st.markdown("### 🎯 Analiz Sonucu", unsafe_allow_html=True)
        
        risk_translation = {
            "Healthy": "Sağlıklı",
            "Mild": "Hafif Risk",
            "Moderate": "Orta Risk",
            "Severe": "Yüksek Risk",
            "None": "Sağlıklı"
        }
        translated_risk = risk_translation.get(risk_label, risk_label)

        if "Healthy" in risk_label or risk_label == "None":
            st.markdown(f"""
            <div class='result-card-healthy'>
                <h2>🎉 {translated_risk}</h2>
                <p>Uyku düzeniniz harika! Risk seviyeniz çok düşük.</p>
                <p><b>{max(pred_proba)*100:.1f}%</b> olasılıkla sağlıklı bir profiliniz var.</p>
            </div>
            """, unsafe_allow_html=True)
        elif "Mild" in risk_label:
            st.markdown(f"""
            <div class='result-card-mild'>
                <h2>⚠️ {translated_risk}</h2>
                <p>Uykunuz fena değil ancak bazı metriklerde dengesizlikler var.</p>
                <p><b>{max(pred_proba)*100:.1f}%</b> olasılıkla hafif bir risk taşıyorsunuz.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='result-card-risk'>
                <h2>🚨 {translated_risk}</h2>
                <p>Uyku verilerinizde ciddi bozukluklar gözlemlendi!</p>
                <p><b>{max(pred_proba)*100:.1f}%</b> olasılıkla ciddi bir uyku rahatsızlığı taşıyorsunuz.</p>
            </div>
            """, unsafe_allow_html=True)
            
        # --- GEMINI AI COACH ---
        st.markdown("### 🤖 Yapay Zeka Uyku Koçu Yorumu")
        with st.spinner("Gemini Yapay Zekası profilinizi değerlendiriyor..."):
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
                
                Lütfen bu hastaya doğrudan hitap ederek ("Merhaba, verilerinizi inceledim..." gibi), 
                uyku kalitesini artırması veya mevcut durumunu koruması için Türkçe, samimi ve motive edici 2-3 paragraflık bir değerlendirme ve tavsiye yazısı oluştur.
                Maddeler kullanabilirsin. Sonucu çok uzun tutma.
                """
                response = model_ai.generate_content(prompt)
                
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.write(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Yapay zeka ile iletişim kurulurken bir hata oluştu: {e}")

        # --- DATA COMPARISON ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Sizin Verileriniz vs Genel Ortalama")
        st.write("Verdiğiniz anahtar değerlerin diğer insanlarla karşılaştırması:")

        compare_features = {
            "Gece Uyanma Sayısı": ("wake_episodes_per_night", user_inputs.get("wake_episodes_per_night", 0)),
            "Uyku Süresi (Saat)": ("sleep_duration_hrs", user_inputs.get("sleep_duration_hrs", 0)),
            "Kafein (mg)": ("caffeine_mg_before_bed", user_inputs.get("caffeine_mg_before_bed", 0)),
            "Uykuya Dalma Süresi": ("sleep_latency_mins", user_inputs.get("sleep_latency_mins", 0)),
            "Stres Skoru": ("stress_score", user_inputs.get("stress_score", 0))
        }

        chart_data = {"Özellik": [], "Senin Değerin": [], "Genel Ortalama": []}

        for label, (col_name, user_val) in compare_features.items():
            chart_data["Özellik"].append(label)
            chart_data["Senin Değerin"].append(user_val)
            chart_data["Genel Ortalama"].append(feature_defaults.get(col_name, 0))

        df_chart = pd.DataFrame(chart_data)
        df_melted = pd.melt(df_chart, id_vars=['Özellik'], value_vars=['Senin Değerin', 'Genel Ortalama'], 
                            var_name='Grup', value_name='Değer')

        fig = plotly_express.bar(df_melted, x="Özellik", y="Değer", color="Grup", barmode="group",
                    color_discrete_sequence=["#00f2fe", "#ff4b2b"],
                    template="plotly_dark")

        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
