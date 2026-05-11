import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
  LineChart, Line
} from 'recharts';
import { 
  Activity, Brain, Coffee, User, Moon, Clock, Calendar, HeartPulse, 
  Bed, Sparkles, CheckCircle2, AlertTriangle, ShieldAlert, Wine,
  Dumbbell, TrendingUp, Info, X, History, Save, Plus, Trash2, ChevronDown
} from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

/* ─── Info Tooltip Component ─── */
const InfoTip = ({ text }: { text: string }) => {
  const [open, setOpen] = useState(false);
  return (
    <span className="info-tip-wrap">
      <button
        type="button"
        className="info-tip-btn"
        onClick={(e) => { e.stopPropagation(); setOpen(!open); }}
        aria-label="Bilgi"
      >
        <Info size={13} />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            className="info-tip-bubble"
            initial={{ opacity: 0, y: 6, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <button className="info-tip-close" onClick={() => setOpen(false)}><X size={12} /></button>
            {text}
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  );
};

/* ─── Form Fields Config ─── */
const TABS = [
  { id: 'profil', label: '👤 Profil', icon: User },
  { id: 'yasam', label: '🏃 Yaşam', icon: Activity },
  { id: 'uyku', label: '🌙 Uyku', icon: Moon },
];

const FIELDS: Record<string, Array<{
  key: string; label: string; icon: any; type: 'number' | 'select'; 
  placeholder?: string; step?: string; hint?: string;
  options?: { value: string; label: string }[];
}>> = {
  profil: [
    { key: 'age', label: 'Yaş', icon: User, type: 'number', placeholder: '25', hint: 'Kendi yaşınızı girin. Örnek: 25, 34, 42' },
    { key: 'bmi', label: 'BMI (Vücut Kitle İndeksi)', icon: Activity, type: 'number', placeholder: '22.5', step: '0.1', hint: 'Kilonuzu (kg) boyunuzun (m) karesine bölün. Örnek: 70kg / 1.75m² = 22.9. Normal aralık: 18.5 – 24.9' },
    { key: 'mental_health_condition', label: 'Ruh Sağlığı', icon: Brain, type: 'select', hint: 'Tanı konmuş veya kendinizde hissettiğiniz ruh sağlığı durumunuzu seçin. Emin değilseniz "Sağlıklı" seçebilirsiniz.', options: [
      { value: '', label: 'Seçiniz...' },
      { value: 'Healthy', label: 'Sağlıklı' },
      { value: 'Anxiety', label: 'Anksiyete' },
      { value: 'Depression', label: 'Depresyon' },
      { value: 'Both', label: 'Anksiyete & Depresyon' },
    ]},
    { key: 'shift_work', label: 'Vardiyalı Çalışma', icon: Calendar, type: 'select', hint: 'Gündüz/gece dönüşümlü vardiyalı bir işte çalışıp çalışmadığınızı seçin.', options: [
      { value: '', label: 'Seçiniz...' },
      { value: '0', label: 'Hayır' },
      { value: '1', label: 'Evet' },
    ]},
  ],
  yasam: [
    { key: 'caffeine_mg_before_bed', label: 'Kafein (mg)', icon: Coffee, type: 'number', placeholder: '60', hint: 'Uyumadan önceki saatlerde aldığınız toplam kafein miktarı. 1 Türk kahvesi ≈ 60mg, 1 filtre kahve ≈ 100mg, 1 çay ≈ 40mg. İçmiyorsanız 0 yazın.' },
    { key: 'alcohol_units_before_bed', label: 'Alkol (birim)', icon: Wine, type: 'number', placeholder: '0', hint: 'Uyumadan önce tüketilen alkol birimi. 1 birim ≈ 1 küçük bira veya 1 kadeh şarap. Kullanmıyorsanız 0 yazın.' },
    { key: 'exercise_day', label: 'Egzersiz Yapıldı mı?', icon: Dumbbell, type: 'select', hint: 'O gün en az 30 dakika düzenli fiziksel aktivite (yürüyüş, koşu, spor vb.) yapıp yapmadığınızı seçin.', options: [
      { value: '', label: 'Seçiniz...' },
      { value: '0', label: 'Hayır' },
      { value: '1', label: 'Evet' },
    ]},
    { key: 'stress_score', label: 'Stres Skoru (0-10)', icon: Brain, type: 'number', placeholder: '5', hint: 'Genel stres seviyeniz. 0 = Hiç stresli değilim, 5 = Orta, 10 = Aşırı stresli. Kendinizi nasıl hissediyorsanız onu girin.' },
  ],
  uyku: [
    { key: 'sleep_duration_hrs', label: 'Uyku Süresi (saat)', icon: Clock, type: 'number', placeholder: '7.5', step: '0.5', hint: 'Geceleri ortalama kaç saat uyuyorsunuz? Yetişkinler için ideal: 7-9 saat. Örnek: 6.5, 7, 8' },
    { key: 'rem_percentage', label: 'REM Yüzdesi (%)', icon: Moon, type: 'number', placeholder: '20', hint: 'REM (Rüya Evresi), uykunun rüya gördüğünüz kısmıdır. Akıllı saatinizden bakabilirsiniz. Bilmiyorsanız %20-25 arası normal bir değer girebilirsiniz.' },
    { key: 'sleep_latency_mins', label: 'Uykuya Dalma (dk)', icon: Bed, type: 'number', placeholder: '15', hint: 'Yatağa yattıktan sonra uykuya dalmanız kaç dakika sürer? Normal: 10-20 dk. 30 dk üzeri uyku zorluğuna işaret edebilir.' },
    { key: 'wake_episodes_per_night', label: 'Gece Uyanma Sayısı', icon: HeartPulse, type: 'number', placeholder: '1', hint: 'Gece boyunca uykunuz ortalama kaç kez bölünüyor? Hiç bölünmüyorsa 0, sık bölünüyorsa 3-4 gibi değerler girebilirsiniz.' },
  ],
};

const INITIAL_STATE: Record<string, string> = {};
Object.values(FIELDS).flat().forEach(f => { INITIAL_STATE[f.key] = ''; });

/* ─── Stagger animation variants ─── */
const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.06 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } }
};

/* ─── Custom Tooltip ─── */
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'rgba(15, 19, 41, 0.95)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '12px',
        padding: '12px 16px',
        backdropFilter: 'blur(10px)',
      }}>
        <p style={{ color: '#f1f5f9', fontWeight: 600, marginBottom: '6px' }}>{label}</p>
        {payload.map((entry: any, i: number) => (
          <p key={i} style={{ color: entry.color, fontSize: '0.85rem' }}>
            {entry.name}: <strong>{entry.value}</strong>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

/* ═══════════════════════════════════════════
   DASHBOARD COMPONENT
   ═══════════════════════════════════════════ */
const Dashboard = () => {
  const { userEmail } = useAuth();
  const [activeTab, setActiveTab] = useState('profil');
  const [formData, setFormData] = useState<Record<string, string>>(INITIAL_STATE);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [missingTabs, setMissingTabs] = useState<string[]>([]);

  // Profile state
  const [profiles, setProfiles] = useState<Record<string, any>>({});
  const [activeProfile, setActiveProfile] = useState<string>('');
  const [newProfileName, setNewProfileName] = useState('');
  const [showNewProfile, setShowNewProfile] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  // Load profiles on mount
  useEffect(() => {
    if (userEmail) {
      axios.get(`${API_BASE_URL}/api/profiles/${userEmail}`)
        .then(res => {
          setProfiles(res.data.profiles || {});
          const names = Object.keys(res.data.profiles || {});
          if (names.length > 0 && !activeProfile) setActiveProfile(names[0]);
        }).catch(() => {});
    }
  }, [userEmail]);

  // Load history when profile changes
  useEffect(() => {
    if (userEmail && activeProfile) {
      axios.get(`${API_BASE_URL}/api/history/${userEmail}/${activeProfile}`)
        .then(res => setHistory(res.data.history || []))
        .catch(() => setHistory([]));
    } else {
      setHistory([]);
    }
  }, [userEmail, activeProfile]);

  // Load profile data into form
  const loadProfile = (name: string) => {
    setActiveProfile(name);
    const data = profiles[name];
    if (data) {
      const newForm = { ...INITIAL_STATE };
      Object.keys(data).forEach(k => { if (k in newForm) newForm[k] = String(data[k]); });
      setFormData(newForm);
      setResult(null);
      setValidationError(null);
    }
  };

  // Save current form as profile
  const saveProfile = async (name: string) => {
    if (!userEmail || !name.trim()) return;
    const data: Record<string, any> = {};
    Object.entries(formData).forEach(([k, v]) => {
      if (v !== '') { const n = Number(v); data[k] = isNaN(n) ? v : n; }
    });
    try {
      const res = await axios.post(`${API_BASE_URL}/api/profiles`, {
        email: userEmail, profile_name: name.trim(), profile_data: data
      });
      setProfiles(res.data.profiles);
      setActiveProfile(name.trim());
      setShowNewProfile(false);
      setNewProfileName('');
    } catch (e) { console.error(e); }
  };

  // Delete profile
  const deleteProfile = async (name: string) => {
    if (!userEmail) return;
    try {
      const res = await axios.delete(`${API_BASE_URL}/api/profiles/${userEmail}/${name}`);
      setProfiles(res.data.profiles);
      if (activeProfile === name) {
        const remaining = Object.keys(res.data.profiles);
        setActiveProfile(remaining.length > 0 ? remaining[0] : '');
      }
    } catch (e) { console.error(e); }
  };

  const handleDeleteHistory = async (logId: number) => {
    if (!window.confirm("Bu geçmiş analizi silmek istediğinize emin misiniz?")) return;
    try {
      await axios.delete(`${API_BASE_URL}/api/history/${logId}`);
      setHistory(prev => prev.filter(h => h.id !== logId));
    } catch (e) {
      console.error("Geçmiş silinemedi", e);
      alert("Silme işlemi başarısız oldu.");
    }
  };

  const handleChange = (key: string, value: string) => {
    setFormData(prev => ({ ...prev, [key]: value }));
    setValidationError(null);
  };

  const handlePredict = async () => {
    const allFields = Object.values(FIELDS).flat();
    const emptyFields = allFields.filter(f => formData[f.key] === '' || formData[f.key] === undefined);
    if (emptyFields.length > 0) {
      const tabsWithMissing = new Set<string>();
      for (const ef of emptyFields) {
        for (const [tabId, fields] of Object.entries(FIELDS)) {
          if (fields.some(f => f.key === ef.key)) tabsWithMissing.add(tabId);
        }
      }
      setMissingTabs(Array.from(tabsWithMissing));
      setValidationError(`Lütfen tüm alanları doldurun. Eksik: ${emptyFields.map(f => f.label).join(', ')}`);
      setActiveTab(Array.from(tabsWithMissing)[0]);
      return;
    }
    setValidationError(null); setMissingTabs([]);
    setLoading(true); setResult(null);
    try {
      const cleaned = Object.fromEntries(
        Object.entries(formData).map(([k, v]) => {
          if (v === '') return [k, null];
          const num = Number(v); return [k, isNaN(num) ? v : num];
        })
      );
      const res = await axios.post(`${API_BASE_URL}/api/predict`, {
        inputs: cleaned, email: userEmail, profile_name: activeProfile || 'default'
      });
      setResult(res.data);
      // Refresh history
      if (userEmail && activeProfile) {
        axios.get(`${API_BASE_URL}/api/history/${userEmail}/${activeProfile}`)
          .then(r => setHistory(r.data.history || [])).catch(() => {});
      }
      // Auto-save profile if active
      if (activeProfile) saveProfile(activeProfile);
    } catch (error: any) {
      alert(`Analiz hatası: ${error.response?.data?.detail || error.message}`);
    } finally { setLoading(false); }
  };

  /* Chart data */
  const chartData = result ? Object.keys(result.chart_data.user_values).map((key) => ({
    name: key,
    Sizin: result.chart_data.user_values[key] || 0,
    Ortalama: result.chart_data.average_values[key] || 0
  })) : [];

  /* Risk styling */
  const getRiskStyle = () => {
    if (!result) return {};
    const rl = result.risk_label;
    if (rl.includes('Healthy') || rl === 'None') return { color: 'var(--success)', bg: 'var(--success-bg)', border: 'var(--success-border)', icon: CheckCircle2, badgeClass: 'result-badge-success' };
    if (rl.includes('Mild')) return { color: 'var(--warning)', bg: 'var(--warning-bg)', border: 'var(--warning-border)', icon: AlertTriangle, badgeClass: 'result-badge-warning' };
    return { color: 'var(--danger)', bg: 'var(--danger-bg)', border: 'var(--danger-border)', icon: ShieldAlert, badgeClass: 'result-badge-danger' };
  };

  const riskStyle = getRiskStyle();

  /* History trend data for LineChart */
  const trendData = [...history].reverse().slice(-14).map(h => ({
    date: (h.created_at || '').slice(5, 10),
    Uyku: h.inputs?.sleep_duration_hrs ?? 0,
    Stres: h.inputs?.stress_score ?? 0,
    Güven: Math.round((h.probability ?? 0) * 100),
  }));

  const profileNames = Object.keys(profiles);

  return (
    <div>
      {/* Hero */}
      <motion.div 
        className="dashboard-hero"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="heading-hero">Uyku Sağlığı Analizi</h1>
        <p className="text-body" style={{ maxWidth: '500px', margin: '0.75rem auto 0' }}>
          Yapay zeka destekli modelimiz verilerinizi analiz ederek kişiselleştirilmiş uyku tavsiyeleri sunar.
        </p>
      </motion.div>

      {/* ═══ PROFILE BAR ═══ */}
      <motion.div
        className="profile-bar"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <div className="profile-bar-left">
          <User size={16} color="var(--accent-tertiary)" />
          <span className="profile-bar-label">Profil:</span>
          {profileNames.map(name => (
            <button
              key={name}
              className={`profile-chip ${activeProfile === name ? 'active' : ''}`}
              onClick={() => loadProfile(name)}
            >
              {name}
              {activeProfile === name && (
                <span className="profile-chip-delete" onClick={e => { e.stopPropagation(); deleteProfile(name); }}>
                  <X size={10} />
                </span>
              )}
            </button>
          ))}
          {!showNewProfile ? (
            <button className="profile-chip profile-chip-add" onClick={() => setShowNewProfile(true)}>
              <Plus size={14} /> Yeni
            </button>
          ) : (
            <span className="profile-new-input-wrap">
              <input
                className="profile-new-input"
                placeholder="Profil adı..."
                value={newProfileName}
                onChange={e => setNewProfileName(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && saveProfile(newProfileName)}
                autoFocus
              />
              <button className="profile-chip active" onClick={() => saveProfile(newProfileName)}>
                <Save size={12} /> Kaydet
              </button>
              <button className="profile-chip" onClick={() => { setShowNewProfile(false); setNewProfileName(''); }}>
                <X size={12} />
              </button>
            </span>
          )}
        </div>
        {activeProfile && (
          <button className="profile-chip active" onClick={() => saveProfile(activeProfile)} title="Mevcut verileri profilde güncelle">
            <Save size={12} /> Güncelle
          </button>
        )}
      </motion.div>

      {/* Form Card */}
      <motion.div 
        className="card card-no-hover" 
        style={{ marginBottom: 'var(--space-xl)' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.15 }}
      >
        {/* Pill Tabs */}
        <div className="tab-nav">
          {TABS.map(tab => (
            <button
              key={tab.id}
              className={`tab-item ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content with AnimatePresence */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            exit={{ opacity: 0, transition: { duration: 0.15 } }}
          >
            <div className="form-grid">
              {FIELDS[activeTab].map(field => (
                <motion.div key={field.key} className={`form-field ${validationError && formData[field.key] === '' ? 'form-field-error' : ''}`} variants={itemVariants}>
                  <label className="form-label">
                    <field.icon size={14} />
                    {field.label}
                    {field.hint && <InfoTip text={field.hint} />}
                  </label>
                  {field.type === 'select' ? (
                    <select
                      className={`form-select ${validationError && formData[field.key] === '' ? 'input-error' : ''}`}
                      value={formData[field.key]}
                      onChange={e => handleChange(field.key, e.target.value)}
                    >
                      {field.options!.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      className={`form-input ${validationError && formData[field.key] === '' ? 'input-error' : ''}`}
                      type="number"
                      step={field.step || 'any'}
                      value={formData[field.key]}
                      onChange={e => handleChange(field.key, e.target.value)}
                      placeholder={field.placeholder}
                    />
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Validation Error */}
        <AnimatePresence>
          {validationError && (
            <motion.div
              className="error-banner"
              style={{ marginTop: 'var(--space-lg)' }}
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
            >
              <AlertTriangle size={16} style={{ flexShrink: 0, marginRight: '8px', verticalAlign: 'middle' }} />
              {validationError}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Submit */}
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: 'var(--space-2xl)' }}>
          <button className="btn btn-primary" onClick={handlePredict} disabled={loading}>
            {loading ? (
              <><div className="spinner" /> Yapay Zeka Analiz Ediyor...</>
            ) : (
              <><Sparkles size={18} /> Analizi Başlat</>
            )}
          </button>
        </div>
      </motion.div>

      {/* ═══ GEÇMİŞ ANALİZLER ═══ */}
      {history.length > 0 && (
        <motion.div 
          className="card card-no-hover"
          style={{ marginBottom: 'var(--space-xl)' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-md)' }}>
            <h3 className="heading-card" style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <History size={18} color="var(--accent-tertiary)" />
              Geçmiş Analiz Kayıtları
            </h3>
            <span className="text-small text-tertiary">Profil: {activeProfile}</span>
          </div>
          <p className="text-body" style={{ fontSize: '0.85rem', marginBottom: 'var(--space-md)' }}>
            Yapay zekayı yanıltmamak adına, hatalı girdiğiniz geçmiş analiz kayıtlarını silebilirsiniz.
          </p>

          <div className="history-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '250px', overflowY: 'auto', paddingRight: '4px' }}>
            {history.map(item => (
              <div key={item.id} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.05)'
              }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <strong style={{ color: 'var(--text-primary)', fontSize: '0.9rem' }}>{item.translated_risk}</strong>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>
                      {new Date(item.created_at).toLocaleString('tr-TR', { dateStyle: 'short', timeStyle: 'short' })}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Uyku: {item.inputs?.sleep_duration_hrs}s, Stres: {item.inputs?.stress_score}/10, Kafein: {item.inputs?.caffeine_mg_before_bed}mg
                  </div>
                </div>
                <button 
                  onClick={() => handleDeleteHistory(item.id)}
                  style={{
                    background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: 'var(--danger)', cursor: 'pointer',
                    padding: '8px', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'}
                  title="Bu kaydı sil"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* ═══ RESULTS – VISUAL SHOW ═══ */}
      <AnimatePresence>
        {result && (() => {
          const rl = result.risk_label;
          const isHealthy = rl.includes('Healthy') || rl === 'None';
          const isMild = rl.includes('Mild');
          const color = isHealthy ? 'var(--success)' : isMild ? 'var(--warning)' : 'var(--danger)';
          const heroClass = isHealthy ? 'healthy' : isMild ? 'mild' : 'risk';
          const badgeClass = isHealthy ? 'result-badge-success' : isMild ? 'result-badge-warning' : 'result-badge-danger';
          const RiskIcon = isHealthy ? CheckCircle2 : isMild ? AlertTriangle : ShieldAlert;
          const pct = Math.round(result.probability * 100);

          // SVG ring math
          const radius = 78;
          const circumference = 2 * Math.PI * radius;
          const offset = circumference - (pct / 100) * circumference;

          // Metric cards config
          const metricItems = [
            { key: 'Uyku Süresi (Saat)', icon: Clock, unit: 'saat', color: '#7c5cfc' },
            { key: 'Stres Skoru', icon: Brain, unit: '/10', color: '#f87171' },
            { key: 'Kafein (mg)', icon: Coffee, unit: 'mg', color: '#fbbf24' },
            { key: 'Uykuya Dalma Süresi', icon: Bed, unit: 'dk', color: '#38bdf8' },
            { key: 'Gece Uyanma Sayısı', icon: HeartPulse, unit: 'kez', color: '#a78bfa' },
          ];

          return (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
            >
              {/* ── Section Divider ── */}
              <div className="results-divider">
                <span className="results-divider-text">Analiz Sonuçları</span>
              </div>

              {/* ── Hero Ring Card ── */}
              <motion.div
                className={`card card-no-hover result-hero ${heroClass}`}
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              >
                <div className={`result-badge ${badgeClass}`} style={{ marginBottom: 'var(--space-lg)' }}>
                  <RiskIcon size={16} />
                  {result.translated_risk}
                </div>

                <div className="ring-container">
                  <svg className="ring-svg" viewBox="0 0 180 180">
                    <circle className="ring-bg" cx="90" cy="90" r={radius} />
                    <motion.circle
                      className="ring-progress"
                      cx="90" cy="90" r={radius}
                      stroke={color}
                      strokeDasharray={circumference}
                      initial={{ strokeDashoffset: circumference }}
                      animate={{ strokeDashoffset: offset }}
                      transition={{ duration: 1.5, ease: [0.22, 1, 0.36, 1], delay: 0.3 }}
                    />
                  </svg>
                  <div className="ring-label">
                    <motion.span
                      className="ring-value"
                      style={{ color }}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.8 }}
                    >
                      {pct}
                    </motion.span>
                    <span className="ring-unit" style={{ color }}>%</span>
                    <span className="ring-sub">Güven Oranı</span>
                  </div>
                </div>

                <p className="text-body" style={{ marginTop: 'var(--space-lg)', maxWidth: '400px' }}>
                  Yapay zeka modelimiz verilerinizi analiz etti ve uyku sağlığınızı <strong style={{ color }}>{result.translated_risk}</strong> olarak değerlendirdi.
                </p>
              </motion.div>

              {/* ── Metric Stat Cards ── */}
              <motion.div
                className="metrics-grid"
                initial="hidden"
                animate="visible"
                variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.08, delayChildren: 0.4 } } }}
              >
                {metricItems.map(item => {
                  const userVal = result.chart_data.user_values[item.key] ?? 0;
                  const avgVal = result.chart_data.average_values[item.key] ?? 0;
                  const maxVal = Math.max(userVal, avgVal, 1);
                  const barWidth = Math.min((userVal / maxVal) * 100, 100);
                  const diff = userVal - avgVal;
                  const diffStr = diff > 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1);
                  const diffColor = item.key === 'Stres Skoru' || item.key === 'Kafein (mg)' || item.key === 'Gece Uyanma Sayısı'
                    ? (diff > 0 ? 'var(--danger)' : 'var(--success)')
                    : (diff > 0 ? 'var(--success)' : 'var(--warning)');

                  return (
                    <motion.div
                      key={item.key}
                      className="metric-card"
                      variants={{
                        hidden: { opacity: 0, y: 20, scale: 0.95 },
                        visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } }
                      }}
                    >
                      <div className="metric-card-header">
                        <div className="metric-card-icon" style={{ background: `${item.color}15` }}>
                          <item.icon size={18} color={item.color} />
                        </div>
                        <div className="metric-card-comparison" style={{ color: diffColor }}>
                          {diff !== 0 && (
                            <>
                              <TrendingUp size={12} style={{ transform: diff < 0 ? 'rotate(180deg)' : 'none' }} />
                              {diffStr}
                            </>
                          )}
                        </div>
                      </div>
                      <div className="metric-card-label">{item.key}</div>
                      <div className="metric-card-value">{userVal}<span style={{ fontSize: '0.8rem', fontWeight: 500, color: 'var(--text-tertiary)', marginLeft: '4px' }}>{item.unit}</span></div>
                      <div className="metric-bar-track">
                        <motion.div
                          className="metric-bar-fill"
                          style={{ background: item.color }}
                          initial={{ width: 0 }}
                          animate={{ width: `${barWidth}%` }}
                          transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1], delay: 0.6 }}
                        />
                      </div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>
                        Ortalama: {avgVal.toFixed(1)}
                      </div>
                    </motion.div>
                  );
                })}
              </motion.div>

              {/* ── AI Coach Section ── */}
              <motion.div
                className="ai-section"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.8 }}
              >
                <div className="card card-no-hover">
                  <div className="ai-header">
                    <div className="ai-avatar">
                      <Sparkles size={24} color="white" />
                    </div>
                    <div className="ai-header-text">
                      <h3>Gemini Uyku Koçu</h3>
                      <p>Yapay zeka destekli kişisel değerlendirme</p>
                    </div>
                  </div>
                  <div className="ai-bubble">
                    {result.ai_feedback.split('\n').filter((p: string) => p.trim()).map((paragraph: string, i: number) => (
                      <motion.p
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 1.0 + i * 0.15 }}
                      >
                        {paragraph}
                      </motion.p>
                    ))}
                  </div>
                </div>
              </motion.div>

              {/* ── Chart Section ── */}
              <motion.div
                className="chart-section"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 1.0 }}
              >
                <div className="card card-no-hover">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                    <TrendingUp color="var(--accent-secondary)" size={20} />
                    <h3 className="heading-card">Detaylı Metrik Karşılaştırması</h3>
                  </div>
                  <div className="chart-wrap">
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={chartData} layout="vertical" margin={{ top: 15, right: 20, left: 0, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                        <XAxis type="number" stroke="var(--text-tertiary)" tick={{ fill: 'var(--text-tertiary)', fontSize: 12 }} />
                        <YAxis type="category" dataKey="name" stroke="var(--text-tertiary)" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} width={120} />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey="Sizin" radius={[0, 6, 6, 0]} barSize={10}>
                          {chartData.map((_: any, i: number) => (
                            <Cell key={i} fill="var(--accent-primary)" />
                          ))}
                        </Bar>
                        <Bar dataKey="Ortalama" fill="rgba(255,255,255,0.12)" radius={[0, 6, 6, 0]} barSize={10} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="chart-legend">
                    <div className="chart-legend-item">
                      <div className="chart-legend-dot" style={{ background: 'var(--accent-primary)' }} /> Sizin Değeriniz
                    </div>
                    <div className="chart-legend-item">
                      <div className="chart-legend-dot" style={{ background: 'rgba(255,255,255,0.15)' }} /> Genel Ortalama
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* ── History Trend ── */}
              {trendData.length > 1 && (
                <motion.div
                  className="chart-section"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 1.2 }}
                >
                  <div className="card card-no-hover">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                      <History color="var(--accent-tertiary)" size={20} />
                      <h3 className="heading-card">Geçmiş Gelişim Trendi</h3>
                      <span className="text-small" style={{ marginLeft: 'auto' }}>Son {trendData.length} analiz · Profil: {activeProfile}</span>
                    </div>
                    <div className="chart-wrap">
                      <ResponsiveContainer width="100%" height={260}>
                        <LineChart data={trendData} margin={{ top: 15, right: 20, left: 0, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                          <XAxis dataKey="date" stroke="var(--text-tertiary)" tick={{ fill: 'var(--text-tertiary)', fontSize: 11 }} />
                          <YAxis stroke="var(--text-tertiary)" tick={{ fill: 'var(--text-tertiary)', fontSize: 11 }} />
                          <Tooltip content={<CustomTooltip />} />
                          <Line type="monotone" dataKey="Uyku" stroke="#7c5cfc" strokeWidth={2} dot={{ r: 3 }} />
                          <Line type="monotone" dataKey="Stres" stroke="#f87171" strokeWidth={2} dot={{ r: 3 }} />
                          <Line type="monotone" dataKey="Güven" stroke="#34d399" strokeWidth={2} dot={{ r: 3 }} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="chart-legend">
                      <div className="chart-legend-item"><div className="chart-legend-dot" style={{ background: '#7c5cfc' }} /> Uyku (saat)</div>
                      <div className="chart-legend-item"><div className="chart-legend-dot" style={{ background: '#f87171' }} /> Stres</div>
                      <div className="chart-legend-item"><div className="chart-legend-dot" style={{ background: '#34d399' }} /> Güven %</div>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          );
        })()}
      </AnimatePresence>
    </div>
  );
};

export default Dashboard;
