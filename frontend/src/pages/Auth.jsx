import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Lock, User, CheckCircle2 } from 'lucide-react';

export default function Auth({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    const endpoint = isLogin ? '/api/login' : '/api/signup';
    
    try {
      const res = await fetch(`http://localhost:3000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        if (isLogin) {
          onLogin(data.token);
          navigate('/dashboard');
        } else {
          setIsLogin(true);
          setError('Signup successful! Please login.');
        }
      } else {
        setError(data.message || 'Authentication failed');
      }
    } catch (err) {
      setError('Server Error. Ensure Node.js server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'var(--bg-main)' }}>
      {/* Left Decoration Panel (Hidden on Mobile) */}
      <div style={{ flex: 1, background: 'linear-gradient(135deg, var(--bg-main), #ecfdf5)', display: 'flex', flexDirection: 'column', padding: '4rem', justifyContent: 'space-between', borderRight: '1px solid var(--border-light)' }} className="hide-on-mobile">
        <div className="logo" onClick={() => navigate('/')} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <Sparkles color="var(--primary)" size={28} /> NutriPlate
        </div>

        <div style={{ maxWidth: '400px' }}>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '1.5rem', color: 'var(--text-main)', lineHeight: 1.2 }}>
            Master your nutrition with intelligent tracking.
          </h2>
          <ul style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem', listStyle: 'none' }}>
             {['Instant AI Food Recognition', 'Precise Macro Calculations', 'Biochemical Bioavailability Modeling', 'ICMR-NIN 2024 Health Scoring'].map((item, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '1.1rem', color: 'var(--text-main)', fontWeight: 500 }}>
                  <CheckCircle2 color="var(--primary)" size={20} /> {item}
                </li>
             ))}
          </ul>
        </div>

        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          © 2026 NutriPlate Inc. All rights reserved.
        </div>
      </div>

      {/* Right Form Panel */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem', position: 'relative', background: 'var(--surface-base)' }}>
        
        {/* Mobile Header */}
        <div className="show-on-mobile" style={{ position: 'absolute', top: '2rem', left: '2rem' }}>
           <div className="logo" onClick={() => navigate('/')} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <Sparkles color="var(--primary)" size={24} /> NutriPlate
          </div>
        </div>

        <motion.div 
          style={{ width: '100%', maxWidth: '420px' }}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ type: "spring", stiffness: 100, damping: 20 }}
        >
          <div style={{ marginBottom: '2.5rem' }}>
             <h2 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
               {isLogin ? 'Welcome back' : 'Create an account'}
             </h2>
             <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem', fontSize: '1.05rem' }}>
               {isLogin ? 'Enter your credentials to access your dashboard.' : 'Start tracking your meals with AI today.'}
             </p>
          </div>

          <AnimatePresence mode="wait">
            <motion.div key={isLogin ? 'login' : 'signup'} initial={{ x: -10, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: 10, opacity: 0 }} transition={{ duration: 0.2 }}>
              
              <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '1.5rem' }}>
                  <label className="input-label">Username</label>
                  <div style={{ position: 'relative' }}>
                    <User size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
                    <input 
                      type="text" 
                      className="input-field" 
                      style={{ paddingLeft: '2.8rem' }}
                      value={username} 
                      onChange={(e) => setUsername(e.target.value)} 
                      placeholder="e.g. user123"
                      required 
                    />
                  </div>
                </div>
                
                <div style={{ marginBottom: '2.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <label className="input-label">Password</label>
                    {isLogin && <button type="button" style={{ background: 'none', border: 'none', color: 'var(--primary)', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}>Forgot password?</button>}
                  </div>
                  <div style={{ position: 'relative' }}>
                    <Lock size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
                    <input 
                      type="password" 
                      className="input-field" 
                      style={{ paddingLeft: '2.8rem' }}
                      value={password} 
                      onChange={(e) => setPassword(e.target.value)} 
                      placeholder="••••••••"
                      required 
                    />
                  </div>
                </div>
                
                {error && (
                  <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ color: error.includes('success') ? '#047857' : '#b91c1c', marginBottom: '1.5rem', fontSize: '0.9rem', background: error.includes('success') ? '#d1fae5' : '#fee2e2', padding: '0.75rem 1rem', borderRadius: '8px', border: `1px solid ${error.includes('success') ? '#a7f3d0' : '#fecaca'}` }}>
                    {error}
                  </motion.div>
                )}
                
                <button type="submit" className="btn" style={{ width: '100%', padding: '0.85rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', fontSize: '1rem' }} disabled={isLoading}>
                  {isLoading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')} 
                  {!isLoading && <ArrowRight size={18} />}
                </button>
              </form>
              
              <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
                  {isLogin ? "Don't have an account? " : "Already have an account? "}
                  <button type="button" style={{ border: 'none', color: 'var(--primary)', background: 'transparent', fontWeight: 600, cursor: 'pointer' }} onClick={() => setIsLogin(!isLogin)}>
                    {isLogin ? 'Sign up' : 'Log in'}
                  </button>
                </p>
              </div>
            </motion.div>
          </AnimatePresence>
        </motion.div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .hide-on-mobile { display: none !important; }
        }
        @media (min-width: 769px) {
          .show-on-mobile { display: none !important; }
        }
      `}</style>
    </div>
  );
}
