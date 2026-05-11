import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { UserPlus, Mail, Lock, ShieldCheck } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Şifreler uyuşmuyor.');
      return;
    }
    
    if (password.length < 6) {
      setError('Şifre en az 6 karakter olmalıdır.');
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API_BASE_URL}/api/auth/register`, { email, password });
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Kayıt başarısız. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="bg-mesh" />
      <div className="bg-mesh-extra" />
      <div className="bg-grid" />

      <div className="auth-page">
        <motion.div 
          className="card auth-card card-no-hover"
          initial={{ opacity: 0, y: 24, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="auth-header">
            <div className="auth-icon">
              <UserPlus size={32} color="white" />
            </div>
            <h1 className="heading-section">Hesap Oluşturun</h1>
            <p className="text-body" style={{ marginTop: '0.5rem' }}>SleepInfo ile uyku sağlığınızı AI'ye analiz ettirin</p>
          </div>

          {error && <div className="error-banner">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-field" style={{ marginBottom: 'var(--space-lg)' }}>
              <label className="form-label"><Mail size={14} /> E-posta</label>
              <input 
                className="form-input"
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="ornek@email.com"
                required 
              />
            </div>

            <div className="form-field" style={{ marginBottom: 'var(--space-lg)' }}>
              <label className="form-label"><Lock size={14} /> Şifre</label>
              <input 
                className="form-input"
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="••••••••"
                required 
              />
            </div>

            <div className="form-field" style={{ marginBottom: 'var(--space-xl)' }}>
              <label className="form-label"><ShieldCheck size={14} /> Şifreyi Onayla</label>
              <input 
                className="form-input"
                type="password" 
                value={confirmPassword} 
                onChange={(e) => setConfirmPassword(e.target.value)} 
                placeholder="••••••••"
                required 
              />
            </div>
            
            <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%' }}>
              {loading ? <><div className="spinner" /> Kayıt Olunuyor...</> : 'Kayıt Ol'}
            </button>
          </form>

          <div className="auth-footer">
            Zaten hesabınız var mı? <Link to="/login">Giriş Yap</Link>
          </div>
        </motion.div>
      </div>
    </>
  );
};

export default Register;
