import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Utensils, Activity, BrainCircuit, ChevronRight, Sparkles, CheckCircle2 } from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.15, delayChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100 } }
  };

  return (
    <div style={{ position: 'relative', overflow: 'hidden', minHeight: '100vh', background: 'var(--bg-main)' }}>
      
      {/* Decorative gradient overlay */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: '600px', 
        background: 'linear-gradient(180deg, #ecfdf5 0%, var(--bg-main) 100%)', zIndex: 0
      }} />

      <header className="app-header" style={{ borderBottom: 'none', background: 'transparent' }}>
        <div className="logo" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles color="var(--primary)" size={24} /> NutriPlate
        </div>
        <button className="btn" onClick={() => navigate('/auth')}>Sign In to Dashboard</button>
      </header>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '6rem 2rem', position: 'relative', zIndex: 10 }}>
        
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          style={{ textAlign: 'center', maxWidth: '850px', margin: '0 auto' }}
        >
          <motion.div variants={itemVariants} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 16px', background: 'var(--surface-base)', border: '1px solid var(--border-light)', borderRadius: '30px', marginBottom: '2rem', color: 'var(--text-main)', fontWeight: 600, boxShadow: 'var(--shadow-sm)', fontSize: '0.9rem' }}>
            <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)' }}></span>
            NutriPlate AI Engine & Bioavailability v2.0 Live
          </motion.div>

          <motion.h1 variants={itemVariants} style={{ fontSize: 'clamp(3.5rem, 6vw, 5.5rem)', fontWeight: 800, marginBottom: '1.5rem', lineHeight: 1.1, color: 'var(--text-main)', letterSpacing: '-0.04em' }}>
            Dietary Intelligence, <br/> 
            <span className="gradient-text">Powered by AI.</span>
          </motion.h1>
          
          <motion.p variants={itemVariants} style={{ fontSize: '1.25rem', color: 'var(--text-muted)', marginBottom: '3rem', lineHeight: 1.6, maxWidth: '650px', margin: '0 auto 3rem auto' }}>
            Instantly calculate nutritional macros through Deep Learning, and evaluate true nutrient bioavailability with our proprietary NutriPlate tracking.
          </motion.p>
          
          <motion.div variants={itemVariants} style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button className="btn" style={{ fontSize: '1.1rem', padding: '1rem 2.5rem', display: 'flex', alignItems: 'center', gap: '8px', borderRadius: '50px' }} onClick={() => navigate('/auth')}>
              Start Analyzing Now <ChevronRight size={20} />
            </button>
          </motion.div>
          
          <motion.div variants={itemVariants} style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginTop: '3rem', color: 'var(--text-muted)', fontSize: '0.9rem', fontWeight: 500 }}>
             <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><CheckCircle2 size={16} color="var(--primary)" /> Highly Accurate</span>
             <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><CheckCircle2 size={16} color="var(--primary)" /> Biochemical Bioavailability</span>
             <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><CheckCircle2 size={16} color="var(--primary)" /> Secure & Private</span>
          </motion.div>
        </motion.div>

        {/* Bento Box Feature Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem', marginTop: '7rem' }}>
          {[
            { icon: <BrainCircuit size={32} color="var(--primary)" />, title: 'YOLOv8 Edge Vision AI', desc: 'Real-time computer vision instance segmentation trained on Indian thalis and multi-dish meals.', bg: '#ecfdf5' },
            { icon: <Activity size={32} color="#2563eb" />, title: 'Biochemical Bioavailability', desc: 'Models promoter & chelator kinetics to compute absorbable iron and zinc beyond raw calorie totals.', bg: '#eff6ff' },
            { icon: <Utensils size={32} color="#f59e0b" />, title: 'NutriPlate DGI Scoring', desc: 'Proprietary ICMR-NIN 2024 algorithms analyzing your dietary ratios to score how balanced your plate is.', bg: '#fffbeb' }
          ].map((feature, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ delay: i * 0.1, duration: 0.5, type: "spring" }}
              className="glass-panel"
              style={{ padding: '2.5rem' }}
            >
              <div style={{ marginBottom: '1.5rem', padding: '16px', background: feature.bg, display: 'inline-block', borderRadius: '16px' }}>
                {feature.icon}
              </div>
              <h3 style={{ fontSize: '1.4rem', marginBottom: '0.8rem', fontWeight: 700, color: 'var(--text-main)' }}>{feature.title}</h3>
              <p style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
}
