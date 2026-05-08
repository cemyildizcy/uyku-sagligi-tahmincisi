# 🌙 Uyku Sağlığı Tahmincisi — Yapay Zeka Destekli Uyku Bozukluğu Risk Analizi

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit)](https://streamlit.io)
[![XGBoost](https://img.shields.io/badge/XGBoost-%2595.3%20Doğruluk-green)](https://xgboost.readthedocs.io)
[![Supabase](https://img.shields.io/badge/Veritabanı-Supabase-3FCF8E?logo=supabase)](https://supabase.com)
[![Gemini AI](https://img.shields.io/badge/Yapay%20Zeka-Google%20Gemini-4285F4?logo=google)](https://ai.google.dev)

> Ham veri analizinden canlı web uygulamasına kadar uçtan uca geliştirilmiş bir makine öğrenimi projesi. Kullanıcının girdiği 13 sağlık ve yaşam tarzı metriğini analiz ederek uyku bozukluğu riskini gerçek zamanlı olarak tahmin eder; ardından yapay zeka tabanlı kişiselleştirilmiş bir uyku koçluğu yorumu sunar.

---

## 🚀 Canlı Demo

> 🔗 **[uykusagligim.streamlit.app](https://uykusagligim.streamlit.app/)** — Uygulamayı Aç

---

## 🎯 Proje Özeti

Bu proje; **veri analizi, model geliştirme ve MLOps** süreçlerinin tamamını kapsayan tam bir Veri Bilimi iş akışını sergiler.

100.000 satırlık bir veri seti üzerinde önce özellik önemi analizi yapılmış, veri sızması (data leakage) kaynaklı metrikler tespit edilerek elenmiş ve sonuç olarak en anlamlı 13 özellik ile XGBoost modeli eğitilmiştir. Model, 5-Katlı Çapraz Doğrulama ile **%95.3 doğruluk oranına** ulaşmıştır.

Tahmin tamamlandıktan sonra **Google Gemini 2.5 Flash** yapay zekası, kullanıcının verilerine özel Türkçe bir uyku koçluğu metni oluşturur.

---

## ✨ Temel Özellikler

| Özellik | Açıklama |
|---|---|
| **🤖 Model Yarışması** | Random Forest, Gradient Boosting ve XGBoost; 5-Katlı Çapraz Doğrulama ile karşılaştırıldı |
| **📊 Özellik Seçimi** | 29 özellik üzerinde önem analizi yapıldı; etkisiz 16 özellik elendi |
| **🔒 Veri Sızması Önleme** | Sonucu "spoileylayan" metrikler (`sleep_quality_score` vb.) eğitimden kasıtlı olarak çıkarıldı |
| **👤 Kullanıcı Kimlik Doğrulama** | `bcrypt` ile şifrelenmiş güvenli Kayıt Ol / Giriş Yap sistemi |
| **☁️ Bulut Veritabanı** | Kullanıcı profilleri Supabase PostgreSQL'e kalıcı olarak kaydedilir |
| **🧠 Yapay Zeka Uyku Koçu** | Google Gemini 2.5 Flash, kullanıcıya özel kişiselleştirilmiş Türkçe tavsiye üretir |
| **💾 Profil Sistemi** | Her hesaba özel uyku metriği profilleri kaydedilebilir ve yüklenebilir |

---

## 🛠️ Teknoloji Yığını

**Makine Öğrenimi ve Veri Bilimi**
- `scikit-learn` — Ön işleme, model değerlendirme (Label Encoding, StandardScaler, Cross-Validation)
- `XGBoost` — Ana sınıflandırıcı (3 model yarışmasının galibi)
- `pandas` / `numpy` — Veri manipülasyonu ve analiz
- `joblib` — Model artifact serileştirme

**Web Uygulaması ve Altyapı**
- `Streamlit` — İnteraktif web arayüzü
- `Supabase` — Bulut PostgreSQL veritabanı (REST API üzerinden)
- `Google Generative AI` — Gemini 2.5 Flash ile kişiselleştirilmiş yapay zeka koçluğu
- `bcrypt` — Güvenli şifre hashleme
- `Plotly` — İnteraktif veri karşılaştırma grafikleri

---

## 📊 Model Geliştirme Süreci

```
100.000 Satırlık Veri Seti
        │
        ▼
Özellik Analizi (29 özellik)
        │
        ▼
Önem Sıralaması → 16 düşük etkili özellik elendi
        │
        ▼
Veri Sızması Tespiti → Sonuç proxy'leri çıkarıldı (sleep_quality_score vb.)
        │
        ▼
3 Model Yarışması (5-Katlı Çapraz Doğrulama)
├── Random Forest:        %93.6 CV Doğruluğu
├── Gradient Boosting:    %92.4 CV Doğruluğu
└── XGBoost:         ✅  %95.3 CV Doğruluğu  ← KAZANAN
        │
        ▼
Final Model: 80.000 satırda eğitildi → 20.000 satırda test edildi
Test Doğruluğu: %95.29
```

---

## 📁 Proje Yapısı

```
uyku-sagligi-tahmincisi/
│
├── app.py                  # Streamlit Arayüzü — Auth, Formlar, Tahmin, Yapay Zeka Koçu
├── train_model.py          # ML Hattı — Eğitim, CV, Artifact dışa aktarma
├── requirements.txt        # Python bağımlılıkları
├── .gitignore              # API anahtarlarını commit'ten korur
│
├── models/                 # Eğitilmiş model dosyaları (otomatik oluşturulur)
│   ├── best_model.joblib
│   ├── scaler.joblib
│   ├── label_encoders.joblib
│   └── ...
│
└── .streamlit/
    └── secrets.toml        # API anahtarları (GitHub'a YÜKLENMEMELİ)
```

---

## ⚙️ Yerel Kurulum

```bash
# 1. Repoyu klonla
git clone https://github.com/cemyildizcy/uyku-sagligi-tahmincisi.git
cd uyku-sagligi-tahmincisi

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Modeli eğit (sleep_health_dataset.csv dosyası gerekli)
python train_model.py

# 4. Gizli anahtar dosyasını oluştur
mkdir .streamlit
# .streamlit/secrets.toml içine aşağıdakileri ekle

# 5. Uygulamayı başlat
streamlit run app.py
```

**`.streamlit/secrets.toml` formatı:**
```toml
SUPABASE_URL = "https://PROJE_ADRESI.supabase.co"
SUPABASE_KEY = "supabase_anahtarin"
GEMINI_API_KEY = "gemini_anahtarin"
```

---

## 🔬 Önemli Tasarım Kararları

1. **Veri Sızması Önleme:** `sleep_quality_score` ve `cognitive_performance_score` gibi özellikler önem sıralamasında ilk 2'de yer almasına rağmen kasıtlı olarak modelden çıkarıldı. Bu metrikler sonucun bir yansıması olduğundan, modele verildiğinde "kopya çekmesine" ve pratikte işe yaramaz hale gelmesine neden oluyor.

2. **Özellik Mühendisliği:** Önem analizi sonrası %1'in altında etkiye sahip 16 özellik (oda sıcaklığı, mevsim, gün tipi vb.) elendi. Kalan 13 özellikli model, 29 özellikli modelle aynı %95.3 doğruluğu elde etti.

3. **Bulut Öncelikli Mimari:** Yerel JSON dosyaları yerine Supabase kullanmak, ücretsiz hosting ortamında sunucu yeniden başlatmalarında kullanıcı verilerinin korunmasını sağlıyor.

---

## 📈 Sonuçlar

| Metrik | Değer |
|---|---|
| Eğitim Veri Seti Boyutu | 100.000 satır |
| Kullanılan Özellik Sayısı | 13 (29'dan seçildi) |
| Çapraz Doğrulama | 5-Katlı |
| En İyi Model | XGBoost |
| Çapraz Doğrulama Doğruluğu | **%95.30** |
| Test Seti Doğruluğu | **%95.29** |

---

## 👤 Geliştirici

**Cem Yıldız**  
*Veri Bilimi ve Makine Öğrenimi Portfolyo Projesi*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Bağlan-blue?logo=linkedin)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-cemyildizcy-black?logo=github)](https://github.com/cemyildizcy)
