# 🌙 Uyku Sağlığı Tahmincisi — Yapay Zeka Destekli Uyku Bozukluğu Risk Analizi

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.x-61DAFB?logo=react)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/XGBoost-%2595.3%20Doğruluk-green)](https://xgboost.readthedocs.io)
[![Supabase](https://img.shields.io/badge/Veritabanı-Supabase-3FCF8E?logo=supabase)](https://supabase.com)
[![Gemini AI](https://img.shields.io/badge/Yapay%20Zeka-Google%20Gemini-4285F4?logo=google)](https://ai.google.dev)

> Ham veri analizinden canlı web uygulamasına kadar uçtan uca geliştirilmiş bir makine öğrenimi projesi. Kullanıcının girdiği 13 sağlık ve yaşam tarzı metriğini analiz ederek uyku bozukluğu riskini gerçek zamanlı olarak tahmin eder; ardından yapay zeka tabanlı kişiselleştirilmiş bir uyku koçluğu yorumu sunar.

---

## 🎯 Proje Özeti

Bu proje; **veri analizi, model geliştirme, full-stack web geliştirme ve MLOps** süreçlerinin tamamını kapsayan tam bir Veri Bilimi ve Web Uygulaması iş akışını sergiler.

100.000 satırlık bir veri seti üzerinde önce özellik önemi analizi yapılmış, veri sızması (data leakage) kaynaklı metrikler tespit edilerek elenmiş ve sonuç olarak en anlamlı 13 özellik ile XGBoost modeli eğitilmiştir. Model, 5-Katlı Çapraz Doğrulama ile **%95.3 doğruluk oranına** ulaşmıştır.

Tahmin tamamlandıktan sonra **Google Gemini 2.5 Flash** yapay zekası, kullanıcının verilerine özel Türkçe bir uyku koçluğu metni oluşturur. Proje modern bir **React + Vite** arayüzü ve **FastAPI** arka ucu ile çalışır.

---

## ✨ Temel Özellikler

| Özellik | Açıklama |
|---|---|
| **🤖 Model Yarışması** | Random Forest, Gradient Boosting ve XGBoost; 5-Katlı Çapraz Doğrulama ile karşılaştırıldı |
| **📊 Özellik Seçimi** | 29 özellik üzerinde önem analizi yapıldı; etkisiz 16 özellik elendi |
| **🔒 Veri Sızması Önleme** | Sonucu "spoileylayan" metrikler (`sleep_quality_score` vb.) eğitimden kasıtlı olarak çıkarıldı |
| **👤 Kullanıcı Kimlik Doğrulama** | `bcrypt` ile şifrelenmiş güvenli Kayıt Ol / Giriş Yap sistemi |
| **☁️ Bulut Veritabanı** | Kullanıcı profilleri ve analiz geçmişi Supabase PostgreSQL'e kalıcı olarak kaydedilir |
| **🧠 Yapay Zeka Uyku Koçu** | Google Gemini 2.5 Flash, kullanıcıya özel kişiselleştirilmiş Türkçe tavsiye üretir |
| **📉 Gelişim Takibi** | Geçmiş analizler kaydedilir ve interaktif grafiklerle zaman içindeki değişim izlenebilir |

---

## 🛠️ Teknoloji Yığını

**Makine Öğrenimi ve Veri Bilimi**
- `scikit-learn` — Ön işleme, model değerlendirme (Label Encoding, StandardScaler, Cross-Validation)
- `XGBoost` — Ana sınıflandırıcı (3 model yarışmasının galibi)
- `pandas` / `numpy` — Veri manipülasyonu ve analiz
- `joblib` — Model artifact serileştirme

**Backend (API & AI)**
- `FastAPI` — Yüksek performanslı REST API
- `Supabase` — Bulut PostgreSQL veritabanı
- `Google Generative AI` — Gemini 2.5 Flash ile kişiselleştirilmiş yapay zeka koçluğu
- `bcrypt` — Güvenli şifre hashleme

**Frontend (Kullanıcı Arayüzü)**
- `React` & `Vite` — Modern, hızlı ve bileşen tabanlı web arayüzü
- `Framer Motion` — Akıcı mikro animasyonlar ve sayfa geçişleri
- `Recharts` — İnteraktif veri karşılaştırma grafikleri ve geçmiş trendleri
- `Lucide React` — Modern ikon seti

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
├── api.py                  # FastAPI Arka Ucu — Auth, Profiller, Geçmiş, Tahmin, Yapay Zeka Koçu
├── train_model.py          # ML Hattı — Eğitim, CV, Artifact dışa aktarma
├── requirements.txt        # Python bağımlılıkları
├── .env                    # API anahtarları (Supabase, Gemini)
│
├── models/                 # Eğitilmiş model dosyaları (joblib formatında)
│
└── frontend/               # React + Vite Kullanıcı Arayüzü
    ├── src/
    │   ├── pages/          # Login, Register, Dashboard
    │   ├── apiConfig.ts    # API URL yapılandırması
    │   ├── index.css       # Özelleştirilmiş dark mode ve glassmorphism stilleri
    │   └── ...
    └── package.json
```

---

## ⚙️ Yerel Kurulum

Bu uygulama Frontend ve Backend olmak üzere iki parçadan oluşmaktadır. İkisini de aynı anda çalıştırmanız gerekir.

### 1. Repoyu Klonlama ve Ayarlar
```bash
git clone https://github.com/cemyildizcy/uyku-sagligi-tahmincisi.git
cd uyku-sagligi-tahmincisi
```

Kök dizinde bir `.env` dosyası oluşturun ve anahtarlarınızı girin:
```env
SUPABASE_URL="https://PROJE_ADRESI.supabase.co"
SUPABASE_KEY="sizin_supabase_anahtariniz"
GEMINI_API_KEY="sizin_gemini_anahtariniz"
```

### 2. Backend'i Çalıştırma (Terminal 1)
```bash
# Python kütüphanelerini yükleyin
pip install -r requirements.txt

# FastAPI sunucusunu başlatın
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend'i Çalıştırma (Terminal 2)
```bash
# Frontend klasörüne girin
cd frontend

# NPM kütüphanelerini yükleyin
npm install

# React geliştirme sunucusunu başlatın
npm run dev
```

Ardından tarayıcınızdan `http://localhost:5173` adresine giderek uygulamayı kullanabilirsiniz.

---

## 🚀 Yayına Alma (Deployment)

Projenin internet üzerinden kesintisiz (7/24) erişilebilir olması için Frontend'i **Vercel**'de, Backend'i ise uykuya dalmayan **Koyeb**'de yayınlayabilirsiniz.

### 1. Backend'i Yayına Alma (Koyeb.com - Uyku Modu Yoktur)
1. [Koyeb.com](https://app.koyeb.com/)'a gidin ve GitHub ile giriş yapıp yeni bir **Web Service** oluşturun.
2. Bu GitHub deponuzu seçin.
3. Ayarlar:
   - **Run Command:** `uvicorn api:app --host 0.0.0.0 --port 8000`
   - **Port:** `8000`
4. **Environment Variables** bölümüne `.env` dosyanızdaki `SUPABASE_URL`, `SUPABASE_KEY` ve `GEMINI_API_KEY` değerlerini girin.
5. Deploy edin ve Koyeb'in size verdiği URL'yi kopyalayın (örn: `https://uyku-api-koyeb.app`).

### 2. Frontend'i Yayına Alma (Vercel.com)
1. [Vercel.com](https://vercel.com)'da **Add New > Project** diyerek bu deponuzu seçin.
2. Ayarlar:
   - **Root Directory:** `frontend` olarak seçin.
   - **Framework Preset:** `Vite`
3. **Environment Variables** bölümüne şu değeri ekleyin:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://uyku-api-koyeb.app` (Koyeb'den aldığınız link)
4. Deploy butonuna tıklayın. Vercel size canlı ve çalışan bir web adresi verecektir.

---

## 🔬 Önemli Tasarım Kararları

1. **Veri Sızması Önleme:** `sleep_quality_score` ve `cognitive_performance_score` gibi özellikler önem sıralamasında ilk 2'de yer almasına rağmen kasıtlı olarak modelden çıkarıldı. Bu metrikler sonucun bir yansıması olduğundan, modele verildiğinde "kopya çekmesine" ve pratikte işe yaramaz hale gelmesine neden oluyor.
2. **Özellik Mühendisliği:** Önem analizi sonrası %1'in altında etkiye sahip 16 özellik (oda sıcaklığı, mevsim, gün tipi vb.) elendi. Kalan 13 özellikli model, 29 özellikli modelle aynı %95.3 doğruluğu elde etti.
3. **Mimarinin Evrimi:** Başlangıçta Streamlit üzerinde çalışan basit bir script olan bu proje, React/Vite arayüzü ve API mimarisi ile baştan yazılarak bulut tabanlı modern bir web uygulamasına dönüştürülmüştür.

---

## 👤 Geliştirici

**Cem Yıldız**  
*Veri Bilimi ve Makine Öğrenimi Portfolyo Projesi*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Bağlan-blue?logo=linkedin)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-cemyildizcy-black?logo=github)](https://github.com/cemyildizcy)
