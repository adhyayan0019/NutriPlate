import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, CheckCircle, Activity, Loader2, LogOut, Image as ImageIcon, Flame, Droplet, Wheat, XCircle, Sparkles, BrainCircuit, Plus, Minus, FileCheck2, Layers, Trash2, Scan, Eye, EyeOff, Edit3, MousePointer, Check, Search, X, Zap, ShieldAlert, Info, Leaf, Coffee, AlertTriangle } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

export default function Dashboard({ onLogout }) {
  const [file, setFile] = useState(null);
  const [previewWidth, setPreviewWidth] = useState(null);
  const [mealType, setMealType] = useState('lunch');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  
  // New States for 2-Step Architecture
  const [verificationData, setVerificationData] = useState(null);
  const [result, setResult] = useState(null);
  const [hoveredFoodIdx, setHoveredFoodIdx] = useState(null);
  const [showSegments, setShowSegments] = useState(true);
  const [isVeg, setIsVeg] = useState(true);
  const [availableClasses, setAvailableClasses] = useState([]);
  
  // Interactive Plate Annotation States
  const [isDrawingMode, setIsDrawingMode] = useState(false);
  const [drawingBox, setDrawingBox] = useState(null);
  const [naturalSize, setNaturalSize] = useState([800, 600]);
  const [pendingNewBox, setPendingNewBox] = useState(null);
  const [newDishName, setNewDishName] = useState('idli');
  const [newDishPortion, setNewDishPortion] = useState(1.0);
  const [newDishSearch, setNewDishSearch] = useState('');
  const [isCustomDishMode, setIsCustomDishMode] = useState(false);
  const [customTypingIdxs, setCustomTypingIdxs] = useState({});
  
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHistory();
    // Fetch all comprehensive Indian food classes for Human-in-the-Loop dropdown
    fetch('http://localhost:3000/api/dishes')
      .then(r => r.json())
      .then(d => {
        if (d.dishes && d.dishes.length > 0) {
          setAvailableClasses(d.dishes);
        } else {
          throw new Error('Fallback to AI classes');
        }
      })
      .catch(() => {
        fetch('http://localhost:8000/classes')
          .then(r => r.json())
          .then(d => {
            if (d.classes && d.classes.length > 0) setAvailableClasses(d.classes);
          })
          .catch(() => {
            setAvailableClasses([
              "aloo gobi", "aloo paratha", "bhindi masala", "biryani", "chaas", 
              "chana masala", "chapati", "chole bhature", "curd / raita", "dal", 
              "dal khichdi", "dhokla", "gajar ka halwa", "gulab jamun", "idli", 
              "jalebi", "kheer", "masala dosa", "mint chutney", "mixed sabzi", 
              "onion salad", "palak paneer", "paneer masala", "papad", "pav bhaji", 
              "poha", "puri bhaji", "rajma chawal", "rasgulla", "rice", "roti", 
              "sabudana khichdi", "salad", "samosa", "thepla", "vada pav"
            ]);
          });
      });
  }, []);

  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setLoadingStep(s => (s + 1) % 4);
      }, 700);
      return () => clearInterval(interval);
    }
  }, [loading]);

  const fetchHistory = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('http://localhost:3000/api/meals', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles.length > 0) {
      const selected = acceptedFiles[0];
      setFile(selected);
      const url = URL.createObjectURL(selected);
      setPreviewWidth(url);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop, 
    accept: {'image/*': []},
    multiple: false
  });

  const clearFile = (e) => {
    if(e) e.stopPropagation();
    setFile(null);
    setPreviewWidth(null);
    setVerificationData(null);
    setResult(null);
  }

  // STEP 1: Upload Image & Get AI Predictions (No DB Save)
  const handleInitialAnalysis = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);
    setVerificationData(null);

    const formData = new FormData();
    formData.append('image', file);
    formData.append('mealType', mealType);
    formData.append('isVeg', isVeg ? 'true' : 'false');

    const token = localStorage.getItem('token');

    try {
      const res = await fetch('http://localhost:3000/api/analyze-image', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      
      setTimeout(() => {
        if (res.ok) {
          const suggested = data.suggestedFoods || [];
          setVerificationData({
             imagePath: data.imagePath,
             foods: suggested,
             isSegmented: data.isSegmented,
             confidenceLevel: data.confidenceLevel
          });
          if (suggested.length > 0) {
            setAvailableClasses(prev => {
              const newNames = suggested.map(f => (f.name || '').toLowerCase()).filter(Boolean);
              return Array.from(new Set([...prev, ...newNames])).sort();
            });
          }
        } else {
          alert(data.message || 'Analysis failed');
        }
        setLoading(false);
      }, 1200);

    } catch (err) {
      alert("Error reaching AI API");
      setLoading(false);
    }
  };

  // STEP 2: Submit Verified Portions for Final NIN Evaluation + Active Learning Logging
  const handleFinalCompute = async () => {
    if (!verificationData) return;
    setLoading(true);

    const token = localStorage.getItem('token');

    // Collect human corrections for active learning
    const feedbacks = (verificationData.foods || [])
      .filter(f => f.corrected && f.originalPrediction)
      .map(f => ({
        original: f.originalPrediction,
        corrected: f.name
      }));

    try {
      const res = await fetch('http://localhost:3000/api/calculate-nutrition', {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify({
           imagePath: verificationData.imagePath,
           mealType,
           foods: verificationData.foods,
           feedbacks: feedbacks
        })
      });
      const data = await res.json();
      
      setTimeout(() => {
        if (res.ok) {
          setResult(data.meal);
          setVerificationData(null); // Clear verification UI
          fetchHistory();
        } else {
          alert(data.message || 'Calculation failed');
        }
        setLoading(false);
      }, 800);

    } catch (err) {
      alert("Error reaching calculation engine");
      setLoading(false);
    }
  };

  const updatePortion = (index, delta) => {
     setVerificationData(prev => {
        if (!prev || !prev.foods || !prev.foods[index]) return prev;
        const newFoods = [...prev.foods];
        const cur = Number(newFoods[index].portion) || 0;
        let next;
        if (delta > 0) {
          next = Math.floor(cur * 2 + 1) / 2;
        } else {
          next = Math.ceil(cur * 2 - 1) / 2;
        }
        const finalPortion = Math.max(0, Math.min(20, parseFloat(next.toFixed(2))));
        newFoods[index] = { ...newFoods[index], portion: finalPortion };
        return { ...prev, foods: newFoods };
     });
  };

  const setPortionDirect = (index, val) => {
     setVerificationData(prev => {
        if (!prev || !prev.foods || !prev.foods[index]) return prev;
        const newFoods = [...prev.foods];
        const parsed = parseFloat(val);
        const finalPortion = isNaN(parsed) ? 0 : Math.max(0, Math.min(20, parseFloat(parsed.toFixed(2))));
        newFoods[index] = { ...newFoods[index], portion: finalPortion };
        return { ...prev, foods: newFoods };
     });
  };

  const handleSvgMouseDown = (e) => {
    if (!isDrawingMode) return;
    e.preventDefault();
    const rect = e.currentTarget.getBoundingClientRect();
    const scaleX = naturalSize[0] / rect.width;
    const scaleY = naturalSize[1] / rect.height;
    const x = Math.round((e.clientX - rect.left) * scaleX);
    const y = Math.round((e.clientY - rect.top) * scaleY);
    setDrawingBox({ startX: x, startY: y, currentX: x, currentY: y });
  };

  const handleSvgMouseMove = (e) => {
    if (!isDrawingMode || !drawingBox) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const scaleX = naturalSize[0] / rect.width;
    const scaleY = naturalSize[1] / rect.height;
    const x = Math.max(0, Math.min(naturalSize[0], Math.round((e.clientX - rect.left) * scaleX)));
    const y = Math.max(0, Math.min(naturalSize[1], Math.round((e.clientY - rect.top) * scaleY)));
    setDrawingBox(prev => ({ ...prev, currentX: x, currentY: y }));
  };

  const handleSvgMouseUp = () => {
    if (!isDrawingMode || !drawingBox) return;
    const x1 = Math.min(drawingBox.startX, drawingBox.currentX);
    const y1 = Math.min(drawingBox.startY, drawingBox.currentY);
    const x2 = Math.max(drawingBox.startX, drawingBox.currentX);
    const y2 = Math.max(drawingBox.startY, drawingBox.currentY);
    setDrawingBox(null);

    if ((x2 - x1) >= 15 && (y2 - y1) >= 15) {
      setPendingNewBox({ box: [x1, y1, x2, y2] });
      setNewDishName(availableClasses.includes('idli') ? 'idli' : (availableClasses[0] || 'idli'));
      setNewDishPortion(1.0);
      setNewDishSearch('');
    }
  };

  const confirmAddPendingBox = () => {
    if (!pendingNewBox || !newDishName) return;
    const cleanDish = newDishName.toLowerCase().trim();
    const newFood = {
      name: cleanDish,
      originalPrediction: pendingNewBox.box ? 'user_drawn' : 'user_added',
      portion: Number(newDishPortion) || 1.0,
      count: 1,
      confidence: 100,
      measure: '1 Serving',
      box: pendingNewBox.box || null,
      imageSize: naturalSize,
      corrected: true,
      isUserAdded: true,
      needsReview: false
    };

    setVerificationData(prev => ({
      ...prev,
      foods: [...(prev?.foods || []), newFood]
    }));

    setAvailableClasses(prev => prev.includes(cleanDish) ? prev : [...prev, cleanDish].sort());

    // Trigger instant IFCT lookup to update measure and calories
    fetch(`http://localhost:3000/api/nutrition/${encodeURIComponent(cleanDish)}`)
      .then(r => r.json())
      .then(data => {
        if (data.nutrition && data.nutrition.measure) {
          setVerificationData(prev => {
            if (!prev || !prev.foods) return prev;
            const updated = prev.foods.map(f => {
              if (f.name === cleanDish && f.measure === '1 Serving') {
                return { ...f, measure: `${data.nutrition.measure} (~${data.nutrition.calories} kcal)` };
              }
              return f;
            });
            return { ...prev, foods: updated };
          });
        }
      })
      .catch(() => {});

    setPendingNewBox(null);
    setIsDrawingMode(false);
  };

  const cancelPendingBox = () => {
    setPendingNewBox(null);
  };

  const DISH_FAMILY_MAP = {
    idli: ['idli', 'rawa idli', 'thatte idli', 'kanchipuram idli'],
    dosa: ['masala dosa', 'dosa', 'rava dosa', 'neer dosa', 'pesarattu', 'set dosa', 'benne dosa'],
    chutney: ['coconut chutney', 'tomato chutney', 'mint chutney', 'peanut chutney', 'tamarind chutney'],
    dal: ['dal tadka', 'dal fry', 'dal makhani', 'sambar', 'moong dal', 'chana dal', 'panchmel dal', 'maa ki dal'],
    sambar: ['sambar', 'rasam', 'tomato rasam', 'mor kulambu'],
    roti: ['chapati', 'roti', 'akki rotti', 'ragi roti', 'missi roti', 'jowar bhakri', 'bajra roti', 'makki ki roti'],
    chapati: ['chapati', 'roti', 'thepla', 'methi thepla', 'rumali roti'],
    naan: ['naan', 'butter naan', 'garlic naan', 'amritsari kulcha', 'paneer kulcha'],
    paratha: ['aloo paratha', 'paneer paratha', 'gobhi paratha', 'mooli paratha', 'laccha paratha'],
    paneer: ['paneer butter masala', 'kadai paneer', 'palak paneer', 'shahi paneer', 'paneer bhurji', 'paneer tikka', 'matar paneer'],
    rice: ['rice', 'jeera rice', 'curd rice', 'lemon rice', 'tomato rice', 'bisi bele bath', 'biryani'],
    biryani: ['biryani', 'chicken biryani', 'mutton biryani', 'veg biryani', 'egg biryani', 'thalassery biryani'],
    pulao: ['veg pulao', 'peas pulao', 'kashmiri pulao', 'jeera rice'],
    khichdi: ['dal khichdi', 'moong dal khichdi', 'sabudana khichdi', 'bajra khichdi'],
    vada: ['medu vada', 'masala vada', 'mysore bonda', 'batata vada', 'sabudana vada', 'dahi vada'],
    puri: ['puri bhaji', 'poori masal', 'bedmi puri', 'luchi', 'pani puri', 'sev puri', 'bhel puri'],
    sabzi: ['mixed sabzi', 'aloo gobi', 'bhindi masala', 'baingan bharta', 'aloo methi', 'sarson ka saag'],
    bhindi: ['bhindi masala', 'kurkuri bhindi', 'bhindi'],
    curry: ['chana masala', 'rajma chawal', 'chole', 'egg curry', 'chicken curry', 'fish curry', 'mutton curry'],
    chicken: ['butter chicken', 'chicken curry', 'chicken tikka', 'tandoori chicken', 'chicken chettinad', 'chicken 65'],
    fish: ['fish curry', 'fish fry', 'goan fish curry', 'macher jhol', 'meen moilee'],
    mutton: ['mutton curry', 'mutton rogan josh', 'mutton keema', 'mutton sukka', 'chettinad mutton curry'],
    salad: ['salad', 'onion salad', 'cucumber salad', 'kachumber salad', 'sprout salad'],
    raita: ['curd / raita', 'boondi raita', 'cucumber raita', 'mix veg raita', 'curd'],
    halwa: ['gajar ka halwa', 'suji halwa', 'sheera', 'moong dal halwa', 'badam halwa', 'atta halwa'],
    laddu: ['besan laddu', 'motichoor laddu', 'boondi laddu', 'atta laddu', 'rava laddu'],
    chaat: ['papdi chaat', 'samosa chaat', 'aloo tikki chaat', 'dahi puri', 'ragda pattice', 'bhel puri'],
    pakora: ['pakora', 'onion pakoda', 'bread pakora', 'mirchi bajji', 'paneer pakora'],
    dhokla: ['dhokla', 'khaman', 'khandvi', 'handvo']
  };

  const getSmartVariants = (currentName, originalPrediction) => {
    const candidates = [currentName, originalPrediction].filter(Boolean);
    
    for (const name of candidates) {
      const clean = name.toLowerCase().trim();
      for (const [family, variants] of Object.entries(DISH_FAMILY_MAP)) {
        if (clean === family || clean.includes(family) || family.includes(clean)) {
          return variants;
        }
      }
    }

    for (const name of candidates) {
      const clean = name.toLowerCase().trim();
      const tokens = clean.split(' ').filter(t => t.length > 2);
      if (tokens.length > 0 && availableClasses && availableClasses.length > 0) {
        const matches = availableClasses
          .filter(c => tokens.some(tok => c.toLowerCase().includes(tok)))
          .slice(0, 6);
        if (matches.length > 1) return matches;
      }
    }

    return [];
  };

  const updateFoodName = (index, newName, closeTyping = false) => {
     if (closeTyping) {
       setCustomTypingIdxs(prev => ({ ...prev, [index]: false }));
     }
     setVerificationData(prev => {
        if (!prev || !prev.foods || !prev.foods[index]) return prev;
        const newFoods = [...prev.foods];
        newFoods[index] = {
           ...newFoods[index],
           name: newName,
           corrected: true,
           needsReview: false
        };
        return { ...prev, foods: newFoods };
     });

     // Asynchronously fetch live IFCT nutrition profile
     if (newName && newName.trim().length >= 3) {
       fetch(`http://localhost:3000/api/nutrition/${encodeURIComponent(newName.trim().toLowerCase())}`)
         .then(r => r.json())
         .then(data => {
           if (data.nutrition && data.nutrition.measure) {
             setVerificationData(prev => {
               if (!prev || !prev.foods || !prev.foods[index]) return prev;
               const newFoods = [...prev.foods];
               newFoods[index] = {
                 ...newFoods[index],
                 measure: `${data.nutrition.measure} (~${data.nutrition.calories} kcal)`
               };
               return { ...prev, foods: newFoods };
             });
           }
         })
         .catch(() => {});
     }
  };

  const addFoodItem = () => {
     setVerificationData(prev => {
        const nextIdx = prev?.foods?.length || 0;
        setCustomTypingIdxs(c => ({ ...c, [nextIdx]: true }));
        return {
           ...prev,
           foods: [
              ...(prev?.foods || []),
              {
                 name: '',
                 portion: 1.0,
                 count: 1,
                 confidence: 100,
                 measure: '1 Serving (100g)',
                 needsReview: false,
                 corrected: true
              }
           ]
        };
     });
  };

  const removeFood = (index) => {
     setVerificationData(prev => ({
        ...prev,
        foods: prev.foods.filter((_, i) => i !== index)
     }));
  };

  // Redesigned accessible chart colors: Emerald, Blue, Amber
  const COLORS = ['#059669', '#3b82f6', '#f59e0b']; 
  const loadingText = ["Initializing Neural Engine...", "Extracting Visual Features...", "Running Output Validation...", "Evaluating against NIN bounds..."];

  return (
    <div>
      <header className="app-header">
        <div className="logo" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles color="var(--primary)" size={24} /> NutriPlate
        </div>
        <button className="btn btn-ghost" onClick={onLogout} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem', padding: '0.6rem 1.2rem' }}>
          <LogOut size={16} /> Logout session
        </button>
      </header>

      <div className="dashboard-layout">
        
        {/* Left Sidebar: Upload & History */}
        <aside className="sidebar">
          
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="glass-panel" style={{ padding: '1.5rem', boxShadow: 'none', border: '1px solid var(--border-light)' }}>
            <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)' }}>
              <Activity size={20} color="var(--primary)" /> Meal Scanner
            </h3>
            
            <div style={{ marginBottom: '1.2rem' }}>
              <label className="input-label">Select Meal Context</label>
              <select className="input-field" value={mealType} onChange={e => setMealType(e.target.value)} style={{ background: '#f8fafc' }} disabled={loading}>
                <option value="breakfast">🍳 Breakfast (~450 kcal)</option>
                <option value="lunch">🍛 Lunch (~650 kcal)</option>
                <option value="dinner">🌙 Dinner (~500 kcal)</option>
                <option value="snack">☕ Snack (~200 kcal)</option>
              </select>
            </div>

            {/* Pure Vegetarian Plate Toggle */}
            <div style={{ marginBottom: '1.2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: isVeg ? '#f0fdf4' : '#f8fafc', borderRadius: '10px', border: isVeg ? '1.5px solid #86efac' : '1px solid #e2e8f0', transition: 'all 0.2s ease' }}>
              <div>
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: isVeg ? '#15803d' : 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  🥗 Pure Vegetarian Plate
                </span>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'block', marginTop: '2px' }}>
                  {isVeg ? 'Excludes all meat/egg detections' : 'Mixed / Non-veg mode'}
                </span>
              </div>
              <input 
                type="checkbox" 
                checked={isVeg} 
                onChange={e => setIsVeg(e.target.checked)} 
                disabled={loading}
                style={{ width: '18px', height: '18px', cursor: 'pointer', accentColor: '#16a34a' }}
                title="Toggle Vegetarian Mode"
              />
            </div>

            <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`} style={{ padding: file ? '1rem' : '2.5rem 1rem', pointerEvents: (verificationData || loading) ? 'none' : 'auto', opacity: (verificationData || loading) ? 0.6 : 1 }}>
              <input {...getInputProps()} />
              
              <AnimatePresence mode="wait">
                {file && previewWidth ? (
                  <motion.div key="preview" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ position: 'relative' }}>
                     <img src={previewWidth} alt="Preview" style={{ width: '100%', height: '180px', objectFit: 'cover', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }} />
                     {!verificationData && !loading && (
                      <button onClick={clearFile} style={{ position: 'absolute', top: '8px', right: '8px', background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '50%', padding: '6px', cursor: 'pointer', color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <XCircle size={18} />
                      </button>
                     )}
                  </motion.div>
                ) : (
                  <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <div style={{ background: '#ecfdf5', width: '64px', height: '64px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.2rem' }}>
                      <UploadCloud size={32} color="var(--primary)" />
                    </div>
                    <p style={{ fontWeight: 600, color: 'var(--text-main)' }}>Drag & drop image</p>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>or click to browse files</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {(!verificationData && !result) && (
              <button className="btn" style={{ width: '100%', marginTop: '1.2rem', padding: '0.9rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }} onClick={handleInitialAnalysis} disabled={!file || loading}>
                {loading ? <><Loader2 className="spinner" size={18} style={{ animation: 'spin 1s linear infinite' }} /> Processing...</> : <><Sparkles size={18} /> Analyze with AI</>}
              </button>
            )}

            {result && (
              <button className="btn btn-ghost" style={{ width: '100%', marginTop: '1.2rem', padding: '0.9rem' }} onClick={() => clearFile()}>Scan Another Meal</button>
            )}
          </motion.div>

          {/* History Timeline */}
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="glass-panel" style={{ padding: '1.5rem', flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', boxShadow: 'none' }}>
            <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>Plate History</h3>
            <div style={{ overflowY: 'auto', flex: 1, paddingRight: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              {history.length === 0 && <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '2rem', fontSize: '0.95rem' }}>No plates scanned yet.</p>}
              
              {history.map((item, i) => (
                <motion.div 
                  key={item._id} 
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                  style={{ padding: '0.8rem', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0', display: 'flex', gap: '1rem', alignItems: 'center' }}
                >
                  <img src={`http://localhost:3000${item.imagePath}`} alt="" style={{ width: '48px', height: '48px', borderRadius: '8px', objectFit: 'cover' }} />
                  <div style={{ flex: 1 }}>
                    <h4 style={{ textTransform: 'capitalize', fontSize: '0.95rem', margin: 0, color: 'var(--text-main)' }}>{item.mealType || 'Meal'}</h4>
                    <div style={{ display: 'flex', gap: '12px', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px', fontWeight: 500 }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Flame size={12} color="var(--accent)" /> {item.nutrition?.calories || 0}</span>
                      <span style={{ color: item.score >= 80 ? 'var(--primary)' : 'var(--text-main)' }}>Score: {item.score || 0}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

        </aside>

        {/* Right Main Content: Results */}
        <main className="main-content">
          <style>{`
            @keyframes spin { 100% { transform: rotate(360deg); } }
            @keyframes pulseSubtle { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.15); opacity: 0.85; } }
            @keyframes cardGlow { 0%, 100% { box-shadow: 0 4px 12px -2px rgba(16, 185, 129, 0.08); } 50% { box-shadow: 0 6px 18px 2px rgba(16, 185, 129, 0.16); } }
          `}</style>
          
          <AnimatePresence mode="wait">
            {loading ? (
               <motion.div key="loading" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                 <div style={{ position: 'relative', width: '100px', height: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <div style={{ position: 'absolute', inset: 0, border: '4px solid #d1fae5', borderRadius: '50%' }} />
                    <div style={{ position: 'absolute', inset: 0, border: '4px solid transparent', borderTopColor: 'var(--primary)', borderRightColor: 'var(--primary)', borderRadius: '50%', animation: 'spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite' }} />
                    <BrainCircuit size={36} color="var(--primary)" />
                 </div>
                 <h2 style={{ marginTop: '2.5rem', fontWeight: 700, fontSize: '1.5rem', color: 'var(--text-main)' }}>Engine Active</h2>
                 <p style={{ color: 'var(--primary)', marginTop: '0.8rem', fontWeight: 500, fontSize: '1rem', background: '#ecfdf5', padding: '0.4rem 1rem', borderRadius: '20px' }}>
                   {loadingText[loadingStep]}
                 </p>
               </motion.div>

            ) : verificationData ? (
               
               <motion.div key="verification" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} style={{ maxWidth: '860px', margin: '0 auto' }}>
                  <header style={{ marginBottom: '1.8rem' }}>
                    <h2 style={{ fontSize: '2rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                      <FileCheck2 color="var(--primary)" size={32} /> User Verification Layer
                    </h2>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', lineHeight: 1.5 }}>
                      Review isolated food dishes and refine portion estimates before running ICMR-NIN nutritional calculations.
                    </p>
                  </header>

                  <div className="glass-panel" style={{ padding: '2rem' }}>
                    
                    {/* Interactive Meal Context Pill Bar */}
                    <div style={{
                      marginBottom: '1.5rem',
                      padding: '1.1rem 1.25rem',
                      background: '#f8fafc',
                      borderRadius: '14px',
                      border: '1.5px solid #e2e8f0'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '8px' }}>
                        <span style={{ fontSize: '0.9rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          🍽️ Select Meal Context for Analysis:
                        </span>
                        <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
                          Calibrates ICMR-NIN 2024 caloric budgets & nutritional targets
                        </span>
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '10px' }}>
                        {[
                          { id: 'breakfast', icon: '🍳', label: 'Breakfast', range: '350–500 kcal', desc: 'Complex carbs & morning PE ratio' },
                          { id: 'lunch', icon: '🍛', label: 'Lunch', range: '550–750 kcal', desc: 'Primary balanced meal with veggies/curd' },
                          { id: 'dinner', icon: '🌙', label: 'Dinner', range: '400–550 kcal', desc: 'Light dinner with strict carb cap' },
                          { id: 'snack', icon: '☕', label: 'Snack', range: '120–250 kcal', desc: 'Healthy nuts, fruits, roasted seeds' }
                        ].map(m => {
                          const isSelected = mealType === m.id;
                          return (
                            <button
                              key={m.id}
                              type="button"
                              onClick={() => setMealType(m.id)}
                              style={{
                                padding: '10px 12px',
                                borderRadius: '10px',
                                border: isSelected ? '2px solid #059669' : '1px solid #cbd5e1',
                                background: isSelected ? '#ecfdf5' : '#ffffff',
                                color: isSelected ? '#065f46' : '#334155',
                                cursor: 'pointer',
                                textAlign: 'left',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '3px',
                                boxShadow: isSelected ? '0 2px 6px rgba(5, 150, 105, 0.15)' : 'none',
                                transition: 'all 0.15s ease'
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <span style={{ fontWeight: 800, fontSize: '0.92rem' }}>{m.icon} {m.label}</span>
                                {isSelected && (
                                  <span style={{ fontSize: '0.7rem', background: '#059669', color: '#ffffff', padding: '1px 6px', borderRadius: '10px', fontWeight: 700 }}>
                                    Active ✓
                                  </span>
                                )}
                              </div>
                              <span style={{ fontSize: '0.75rem', color: isSelected ? '#047857' : '#64748b', fontWeight: 600 }}>
                                Budget: {m.range}
                              </span>
                              <span style={{ fontSize: '0.71rem', color: '#94a3b8', lineHeight: 1.2 }}>
                                {m.desc}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {/* Plate Preview & Interactive Bounding Box Annotation Toolbar */}
                    {(previewWidth || verificationData.imagePath) && (
                      <div style={{ marginBottom: '1.8rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem 1.2rem', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px 12px 0 0', flexWrap: 'wrap', gap: '10px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <Layers size={20} color="#059669" />
                            <div>
                              <span style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f172a' }}>
                                Plate Layout & Dish Separation ({verificationData.foods.length} items)
                              </span>
                              <p style={{ margin: 0, fontSize: '0.78rem', color: '#64748b' }}>
                                Click "Draw Box" below to manually outline and name any dish on your plate.
                              </p>
                            </div>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            {/* Manual Add Dish Button */}
                            <button 
                              type="button"
                              onClick={() => {
                                setPendingNewBox({ box: null });
                                setNewDishName(availableClasses.includes('fried egg') ? 'fried egg' : (availableClasses[0] || 'dal'));
                                setNewDishPortion(1.0);
                                setNewDishSearch('');
                              }}
                              style={{ 
                                background: '#ffffff', 
                                border: '1.5px solid #10b981', 
                                borderRadius: '8px', 
                                padding: '6px 14px', 
                                fontSize: '0.85rem', 
                                fontWeight: 700, 
                                color: '#059669', 
                                cursor: 'pointer', 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: '6px',
                                boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                                transition: 'all 0.15s ease'
                              }}
                              title="Add any food or dish from the IFCT dataset or custom food without drawing"
                            >
                              <Plus size={15} /> + Add Dish to Plate
                            </button>

                            {/* Toggle Draw Box Mode */}
                            <button 
                              type="button"
                              onClick={() => setIsDrawingMode(prev => !prev)} 
                              style={{ 
                                background: isDrawingMode ? '#059669' : '#ffffff', 
                                border: isDrawingMode ? '1.5px solid #047857' : '1px solid #cbd5e1', 
                                borderRadius: '8px', 
                                padding: '6px 14px', 
                                fontSize: '0.85rem', 
                                fontWeight: 700, 
                                color: isDrawingMode ? '#ffffff' : '#059669', 
                                cursor: 'pointer', 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: '6px',
                                boxShadow: isDrawingMode ? '0 0 0 3px rgba(16, 185, 129, 0.25)' : 'none',
                                transition: 'all 0.15s ease'
                              }}
                              title="Click and drag directly on the plate photo to box and name any food"
                            >
                              <Edit3 size={15} />
                              {isDrawingMode ? 'Drawing Active (Drag on Image)' : '✏️ Draw Box on Plate'}
                            </button>

                            <button 
                              type="button"
                              onClick={() => setShowSegments(s => !s)} 
                              style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '6px 12px', fontSize: '0.82rem', fontWeight: 600, color: '#475569', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
                            >
                              {showSegments ? <><EyeOff size={15}/> Hide Boxes</> : <><Eye size={15}/> Show Boxes</>}
                            </button>
                          </div>
                        </div>

                        {/* Interactive Plate Canvas Overlay */}
                        <div style={{ position: 'relative', width: '100%', background: '#090d16', borderRadius: '0 0 14px 14px', overflow: 'hidden', border: '1px solid #e2e8f0', borderTop: 'none', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '12px 0' }}>
                          <div style={{ position: 'relative', display: 'inline-block', maxWidth: '100%', maxHeight: '380px', lineHeight: 0 }}>
                            <img 
                              src={previewWidth || `http://localhost:3000${verificationData.imagePath}`} 
                              alt="Segmented Plate" 
                              onLoad={(e) => {
                                if (e.target.naturalWidth && e.target.naturalHeight) {
                                  setNaturalSize([e.target.naturalWidth, e.target.naturalHeight]);
                                }
                              }}
                              style={{ maxHeight: '380px', maxWidth: '100%', width: 'auto', height: 'auto', objectFit: 'contain', display: 'block', borderRadius: '8px', userSelect: 'none' }}
                              draggable={false}
                            />

                            {showSegments && (
                              <svg 
                                viewBox={`0 0 ${naturalSize[0]} ${naturalSize[1]}`}
                                onMouseDown={handleSvgMouseDown}
                                onMouseMove={handleSvgMouseMove}
                                onMouseUp={handleSvgMouseUp}
                                style={{ 
                                  position: 'absolute', 
                                  inset: 0, 
                                  width: '100%', 
                                  height: '100%', 
                                  cursor: isDrawingMode ? 'crosshair' : 'default',
                                  userSelect: 'none'
                                }}
                              >
                                {verificationData.foods.map((food, idx) => {
                                  if (!food.box) return null;
                                  const [x1, y1, x2, y2] = food.box;
                                  const isHovered = hoveredFoodIdx === idx;
                                  const strokeColor = isHovered ? '#10b981' : (food.isUserAdded ? '#f59e0b' : '#3b82f6');
                                  const fillColor = isHovered ? 'rgba(16, 185, 129, 0.3)' : (food.isUserAdded ? 'rgba(245, 158, 11, 0.22)' : 'rgba(59, 130, 246, 0.18)');
                                  const boxWidth = Math.max(10, x2 - x1);
                                  const boxHeight = Math.max(10, y2 - y1);
                                  const tagWidth = Math.min(320, Math.max(160, boxWidth * 0.75));
                                  const tagY = Math.max(0, y1 - 32);

                                  return (
                                    <g 
                                      key={idx}
                                      onMouseEnter={() => setHoveredFoodIdx(idx)}
                                      onMouseLeave={() => setHoveredFoodIdx(null)}
                                      style={{ cursor: 'pointer' }}
                                    >
                                      <rect 
                                        x={x1} y={y1} width={boxWidth} height={boxHeight}
                                        fill={fillColor}
                                        stroke={strokeColor}
                                        strokeWidth={isHovered ? 6 : 3}
                                        rx="8"
                                      />
                                      <rect 
                                        x={x1} y={tagY} width={tagWidth} height="30"
                                        fill={strokeColor}
                                        rx="6"
                                      />
                                      <text 
                                        x={x1 + 8} y={tagY + 20}
                                        fill="#ffffff"
                                        fontSize="15"
                                        fontWeight="700"
                                      >
                                        {food.name} (x{food.portion})
                                      </text>
                                    </g>
                                  );
                                })}

                                {/* Live In-Progress Drawing Rectangle */}
                                {drawingBox && (
                                  <rect 
                                    x={Math.min(drawingBox.startX, drawingBox.currentX)}
                                    y={Math.min(drawingBox.startY, drawingBox.currentY)}
                                    width={Math.abs(drawingBox.currentX - drawingBox.startX)}
                                    height={Math.abs(drawingBox.currentY - drawingBox.startY)}
                                    fill="rgba(16, 185, 129, 0.25)"
                                    stroke="#10b981"
                                    strokeWidth="4"
                                    strokeDasharray="8 4"
                                    rx="6"
                                  />
                                )}
                              </svg>
                            )}

                          </div>
                        </div>
                      </div>
                    )}

                    {/* Spacious Viewport-Centered Dish Naming & Add Dialog Modal */}
                    {pendingNewBox && (
                      <div style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(15, 23, 42, 0.75)',
                        backdropFilter: 'blur(8px)',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        padding: '1.5rem',
                        zIndex: 99999
                      }}>
                        <div style={{
                          background: '#ffffff',
                          borderRadius: '20px',
                          padding: '2rem',
                          maxWidth: '480px',
                          width: '100%',
                          maxHeight: '90vh',
                          overflowY: 'auto',
                          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.4)',
                          textAlign: 'left'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem' }}>
                            <h4 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span>🍽️</span> {pendingNewBox.box ? 'Name Selected Plate Region' : 'Add Food Item to Plate'}
                            </h4>
                            <button 
                              type="button" 
                              onClick={cancelPendingBox} 
                              style={{ background: '#f1f5f9', border: 'none', borderRadius: '50%', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#64748b' }}
                            >
                              <X size={18} />
                            </button>
                          </div>

                          {/* Mode Tabs: IFCT Master Dishes vs Type Custom Food */}
                          <div style={{ display: 'flex', background: '#f1f5f9', padding: '4px', borderRadius: '10px', marginBottom: '1.2rem' }}>
                            <button
                              type="button"
                              onClick={() => setIsCustomDishMode(false)}
                              style={{
                                flex: 1,
                                padding: '8px 0',
                                borderRadius: '8px',
                                border: 'none',
                                background: !isCustomDishMode ? '#ffffff' : 'transparent',
                                color: !isCustomDishMode ? '#0f172a' : '#64748b',
                                fontWeight: !isCustomDishMode ? 700 : 500,
                                fontSize: '0.85rem',
                                cursor: 'pointer',
                                boxShadow: !isCustomDishMode ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                                transition: 'all 0.15s ease'
                              }}
                            >
                              📋 IFCT Master Dishes ({availableClasses.length || 480})
                            </button>
                            <button
                              type="button"
                              onClick={() => setIsCustomDishMode(true)}
                              style={{
                                flex: 1,
                                padding: '8px 0',
                                borderRadius: '8px',
                                border: 'none',
                                background: isCustomDishMode ? '#ffffff' : 'transparent',
                                color: isCustomDishMode ? '#059669' : '#64748b',
                                fontWeight: isCustomDishMode ? 700 : 500,
                                fontSize: '0.85rem',
                                cursor: 'pointer',
                                boxShadow: isCustomDishMode ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                                transition: 'all 0.15s ease'
                              }}
                            >
                              ✏️ Type Custom Food
                            </button>
                          </div>

                          {!isCustomDishMode ? (
                            <>
                              {/* Filter / Search Bar */}
                              <div style={{ position: 'relative', marginBottom: '1rem' }}>
                                <input 
                                  type="text"
                                  placeholder="Search dishes (e.g. fried egg, dal, roti, dosa)..."
                                  value={newDishSearch}
                                  onChange={(e) => setNewDishSearch(e.target.value)}
                                  style={{
                                    width: '100%',
                                    padding: '9px 12px 9px 36px',
                                    borderRadius: '10px',
                                    border: '1.5px solid #cbd5e1',
                                    fontSize: '0.92rem',
                                    outline: 'none',
                                    boxSizing: 'border-box'
                                  }}
                                  autoFocus
                                />
                                <Search size={18} color="#94a3b8" style={{ position: 'absolute', left: '11px', top: '11px' }} />
                              </div>

                              {/* Select Dish */}
                              <div style={{ marginBottom: '1.2rem' }}>
                                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#475569', marginBottom: '6px' }}>
                                  Select Recognized IFCT Dish:
                                </label>
                                <select 
                                  value={newDishName}
                                  onChange={(e) => setNewDishName(e.target.value)}
                                  size={5}
                                  style={{
                                    width: '100%',
                                    padding: '8px',
                                    borderRadius: '10px',
                                    border: '1.5px solid #cbd5e1',
                                    fontSize: '0.92rem',
                                    fontWeight: 600,
                                    textTransform: 'capitalize',
                                    outline: 'none',
                                    boxSizing: 'border-box'
                                  }}
                                >
                                  {availableClasses
                                    .filter(c => !newDishSearch || c.toLowerCase().includes(newDishSearch.toLowerCase()))
                                    .map(clsName => (
                                      <option key={clsName} value={clsName} style={{ padding: '6px 10px', borderRadius: '4px', cursor: 'pointer' }}>
                                        {clsName.charAt(0).toUpperCase() + clsName.slice(1)}
                                      </option>
                                    ))}
                                </select>
                              </div>
                            </>
                          ) : (
                            <div style={{ marginBottom: '1.2rem' }}>
                              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#475569', marginBottom: '6px' }}>
                                Enter Custom Food / Dish Name:
                              </label>
                              <input 
                                type="text"
                                placeholder="e.g. Fried Egg, Ragi Mudde, Avial, Dhokla..."
                                value={newDishName}
                                onChange={(e) => setNewDishName(e.target.value)}
                                style={{
                                  width: '100%',
                                  padding: '10px 12px',
                                  borderRadius: '10px',
                                  border: '1.5px solid #059669',
                                  fontSize: '0.98rem',
                                  fontWeight: 600,
                                  outline: 'none',
                                  boxSizing: 'border-box'
                                }}
                                autoFocus
                              />
                              <p style={{ margin: '6px 0 0 0', fontSize: '0.78rem', color: '#64748b', lineHeight: 1.4 }}>
                                💡 Model will automatically fetch authentic IFCT 2017 nutritional metrics and permanently remember this dish for active learning.
                              </p>
                            </div>
                          )}

                          {/* Portion Multiplier */}
                          <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#475569', marginBottom: '6px' }}>
                              Portion Serving Multiplier:
                            </label>
                            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                              {[0.5, 1, 1.5, 2].map((p) => (
                                <button
                                  key={p}
                                  type="button"
                                  onClick={() => setNewDishPortion(p)}
                                  style={{
                                    flex: 1,
                                    padding: '7px 0',
                                    borderRadius: '8px',
                                    border: newDishPortion === p ? '1.5px solid #059669' : '1px solid #cbd5e1',
                                    background: newDishPortion === p ? '#ecfdf5' : '#ffffff',
                                    color: newDishPortion === p ? '#065f46' : '#475569',
                                    fontWeight: 700,
                                    fontSize: '0.88rem',
                                    cursor: 'pointer'
                                  }}
                                >
                                  {p}x
                                </button>
                              ))}
                              <input 
                                type="number"
                                min="0"
                                max="10"
                                step="0.25"
                                value={newDishPortion}
                                onChange={(e) => setNewDishPortion(parseFloat(e.target.value) || 0)}
                                style={{
                                  width: '60px',
                                  padding: '6px',
                                  borderRadius: '8px',
                                  border: '1px solid #cbd5e1',
                                  textAlign: 'center',
                                  fontSize: '0.9rem',
                                  fontWeight: 700
                                }}
                              />
                            </div>
                          </div>

                          {/* Actions */}
                          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                            <button 
                              type="button"
                              onClick={cancelPendingBox}
                              style={{ padding: '9px 18px', borderRadius: '10px', border: '1px solid #cbd5e1', background: '#f8fafc', color: '#475569', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer' }}
                            >
                              Cancel
                            </button>
                            <button 
                              type="button"
                              onClick={confirmAddPendingBox}
                              style={{ padding: '9px 20px', borderRadius: '10px', border: 'none', background: '#059669', color: '#ffffff', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', boxShadow: '0 2px 4px rgba(5, 150, 105, 0.3)' }}
                            >
                              <Check size={18} /> Add to Plate
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Food Items List */}
                    {verificationData.foods.length === 0 ? (
                      <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>No foods detected. Please try uploading a clearer image.</div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {verificationData.foods.map((food, idx) => (
                           <div 
                             key={idx} 
                             onMouseEnter={() => setHoveredFoodIdx(idx)}
                             onMouseLeave={() => setHoveredFoodIdx(null)}
                             style={{ 
                               display: 'flex', 
                               alignItems: 'center', 
                               justifyContent: 'space-between', 
                               padding: '1.2rem 1.4rem', 
                               background: hoveredFoodIdx === idx ? '#f0fdf4' : '#f8fafc', 
                               borderRadius: '12px', 
                               border: hoveredFoodIdx === idx ? '1.5px solid #10b981' : '1px solid #e2e8f0',
                               transition: 'all 0.2s ease',
                               flexWrap: 'wrap',
                               gap: '12px'
                             }}
                           >
                              <div style={{ flex: 1, minWidth: '240px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                                  {/* Human-in-the-Loop Editable Dish Selector (Dropdown or Manual Typing) */}
                                  {customTypingIdxs[idx] ? (
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                      <input 
                                        type="text"
                                        value={food.name}
                                        onChange={(e) => updateFoodName(idx, e.target.value, false)}
                                        onKeyDown={(e) => {
                                          if (e.key === 'Enter') {
                                            setCustomTypingIdxs(prev => ({ ...prev, [idx]: false }));
                                          }
                                        }}
                                        placeholder="Type custom food name..."
                                        style={{
                                          fontSize: '0.95rem',
                                          fontWeight: 700,
                                          color: 'var(--text-main)',
                                          background: '#ffffff',
                                          border: '2px solid #059669',
                                          borderRadius: '8px',
                                          padding: '5px 10px',
                                          outline: 'none',
                                          width: '190px',
                                          textTransform: 'capitalize',
                                          boxShadow: '0 0 0 3px rgba(5, 150, 105, 0.15)'
                                        }}
                                        autoFocus
                                      />
                                      <button
                                        type="button"
                                        onClick={() => setCustomTypingIdxs(prev => ({ ...prev, [idx]: false }))}
                                        style={{
                                          padding: '5px 10px',
                                          fontSize: '0.78rem',
                                          fontWeight: 700,
                                          borderRadius: '6px',
                                          border: '1px solid #059669',
                                          background: '#ecfdf5',
                                          color: '#065f46',
                                          cursor: 'pointer'
                                        }}
                                        title="Save and switch to list"
                                      >
                                        ✓ Done
                                      </button>
                                    </div>
                                  ) : (
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                      <select 
                                        value={food.name}
                                        onChange={(e) => {
                                          if (e.target.value === '__custom__') {
                                            setCustomTypingIdxs(prev => ({ ...prev, [idx]: true }));
                                          } else {
                                            updateFoodName(idx, e.target.value, true);
                                          }
                                        }}
                                        style={{
                                          fontSize: '0.95rem',
                                          fontWeight: 700,
                                          color: food.needsReview ? '#b45309' : 'var(--text-main)',
                                          background: food.needsReview ? '#fef3c7' : '#ffffff',
                                          border: food.needsReview ? '1.5px solid #f59e0b' : '1px solid #cbd5e1',
                                          borderRadius: '8px',
                                          padding: '5px 10px',
                                          cursor: 'pointer',
                                          textTransform: 'capitalize',
                                          outline: 'none',
                                          maxWidth: '210px'
                                        }}
                                        title="Select food class or click 'Type Custom' to enter any dish"
                                      >
                                        <option value="__custom__">✏️ + Type Custom Food...</option>
                                        {!availableClasses.includes((food.name || '').toLowerCase()) && food.name && (
                                          <option value={food.name}>{(food.name.charAt(0).toUpperCase() + food.name.slice(1))}</option>
                                        )}
                                        {availableClasses.map(clsName => (
                                          <option key={clsName} value={clsName}>
                                            {clsName.charAt(0).toUpperCase() + clsName.slice(1)}
                                          </option>
                                        ))}
                                      </select>
                                      
                                      <button
                                        type="button"
                                        onClick={() => setCustomTypingIdxs(prev => ({ ...prev, [idx]: true }))}
                                        style={{
                                          padding: '5px 8px',
                                          fontSize: '0.75rem',
                                          fontWeight: 600,
                                          borderRadius: '6px',
                                          border: '1px solid #a7f3d0',
                                          background: '#ecfdf5',
                                          color: '#065f46',
                                          cursor: 'pointer',
                                          display: 'flex',
                                          alignItems: 'center',
                                          gap: '3px'
                                        }}
                                        title="Type any custom food not present in dataset"
                                      >
                                        <Edit3 size={12} /> Type Custom
                                      </button>
                                    </div>
                                  )}

                                  {food.corrected && (
                                    <span style={{ fontSize: '0.72rem', fontWeight: 700, background: '#dcfce7', color: '#15803d', padding: '2px 8px', borderRadius: '12px' }}>
                                      ✓ Corrected
                                    </span>
                                  )}

                                  {food.needsReview && !food.corrected && (
                                    <span style={{ fontSize: '0.72rem', fontWeight: 700, background: '#fef3c7', color: '#b45309', padding: '2px 8px', borderRadius: '12px' }}>
                                      ⚠ Please Confirm
                                    </span>
                                  )}

                                  {food.count > 1 && (
                                    <span style={{ fontSize: '0.72rem', fontWeight: 700, background: '#dbeafe', color: '#1d4ed8', padding: '2px 8px', borderRadius: '12px' }}>
                                      {food.count} items
                                    </span>
                                  )}
                                  {food.areaRatio > 0 && (
                                    <span style={{ fontSize: '0.72rem', fontWeight: 600, background: '#f3e8ff', color: '#7e22ce', padding: '2px 8px', borderRadius: '12px' }}>
                                      {Math.round(food.areaRatio * 100)}% plate
                                    </span>
                                  )}
                                </div>

                                <div style={{ display: 'flex', gap: '8px', marginTop: '6px', alignItems: 'center', flexWrap: 'wrap' }}>
                                  <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', background: '#e2e8f0', padding: '2px 8px', borderRadius: '4px' }}>
                                    IFCT: {food.measure}
                                  </span>
                                  <span style={{ fontSize: '0.82rem', color: food.needsReview ? '#d97706' : '#059669', fontWeight: 600 }}>
                                    {Math.round(food.confidence)}% confidence
                                  </span>
                                </div>

                                {/* Smart IFCT Variant Quick-Pills */}
                                {(() => {
                                  const variants = getSmartVariants(food.name, food.originalPrediction);
                                  if (!variants || variants.length <= 1) return null;
                                  return (
                                    <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '5px', flexWrap: 'wrap' }}>
                                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748b' }}>
                                        💡 Quick Variant:
                                      </span>
                                      {variants.map(v => {
                                        const isCurrent = (food.name || '').toLowerCase().trim() === v.toLowerCase().trim();
                                        return (
                                          <button
                                            key={v}
                                            type="button"
                                            onClick={() => updateFoodName(idx, v, true)}
                                            style={{
                                              padding: '2px 8px',
                                              fontSize: '0.73rem',
                                              fontWeight: isCurrent ? 700 : 500,
                                              borderRadius: '12px',
                                              border: isCurrent ? '1.5px solid #059669' : '1px solid #cbd5e1',
                                              background: isCurrent ? '#dcfce7' : '#ffffff',
                                              color: isCurrent ? '#065f46' : '#334155',
                                              cursor: 'pointer',
                                              textTransform: 'capitalize',
                                              transition: 'all 0.15s ease'
                                            }}
                                            title={`Select ${v} from IFCT Master database`}
                                          >
                                            {isCurrent && '✓ '}{v}
                                          </button>
                                        );
                                      })}
                                    </div>
                                  );
                                })()}
                              </div>
                              
                              {/* Enhanced Portion Multiplier with Presets, Manual Typing, and Clean Stepper */}
                              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
                                {/* Quick Preset Buttons */}
                                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, marginRight: '2px' }}>Presets:</span>
                                  {[0.5, 1, 1.5, 2].map((presetVal) => {
                                    const isSelected = Number(food.portion) === presetVal;
                                    return (
                                      <button
                                        key={presetVal}
                                        type="button"
                                        onClick={() => setPortionDirect(idx, presetVal)}
                                        style={{
                                          padding: '2px 7px',
                                          fontSize: '0.75rem',
                                          fontWeight: 700,
                                          borderRadius: '6px',
                                          border: isSelected ? '1.5px solid #059669' : '1px solid #cbd5e1',
                                          background: isSelected ? '#dcfce7' : '#ffffff',
                                          color: isSelected ? '#15803d' : '#475569',
                                          cursor: 'pointer',
                                          transition: 'all 0.15s ease'
                                        }}
                                        title={`Set portion to ${presetVal}x`}
                                      >
                                        {presetVal}x
                                      </button>
                                    );
                                  })}
                                </div>

                                {/* Stepper + Direct Manual Typing Input */}
                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                  <div style={{ display: 'flex', alignItems: 'center', background: '#ffffff', border: '1.5px solid #cbd5e1', borderRadius: '8px', padding: '3px 6px', gap: '4px' }}>
                                     <button 
                                       type="button"
                                       onClick={() => updatePortion(idx, -0.5)} 
                                       style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', color: food.portion <= 0 ? '#cbd5e1' : 'var(--text-muted)' }}
                                       title="Decrease portion by 0.5 (can reach 0)"
                                     >
                                       <Minus size={15} />
                                     </button>

                                     <div style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                                       <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)' }}>x</span>
                                       <input 
                                         type="number"
                                         min="0"
                                         max="20"
                                         step="0.25"
                                         value={food.portion}
                                         onChange={(e) => setPortionDirect(idx, e.target.value)}
                                         style={{
                                           width: '54px',
                                           padding: '3px 4px',
                                           borderRadius: '4px',
                                           border: '1px solid #e2e8f0',
                                           fontWeight: 800,
                                           fontSize: '0.92rem',
                                           textAlign: 'center',
                                           color: 'var(--text-main)',
                                           background: '#f8fafc',
                                           outline: 'none'
                                         }}
                                         title="Type custom portion multiplier directly (e.g. 0, 0.5, 1, 1.5, 2)"
                                       />
                                     </div>

                                     <button 
                                       type="button"
                                       onClick={() => updatePortion(idx, 0.5)} 
                                       style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', color: 'var(--text-main)' }}
                                       title="Increase portion by 0.5"
                                     >
                                       <Plus size={15} />
                                     </button>
                                  </div>

                                  <button 
                                    type="button"
                                    onClick={() => removeFood(idx)}
                                    style={{ background: '#fee2e2', border: 'none', borderRadius: '8px', padding: '8px', cursor: 'pointer', color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                                    title="Remove item"
                                  >
                                    <Trash2 size={16} />
                                  </button>
                                </div>
                              </div>
                           </div>
                        ))}

                        {/* Add Missing Food Item Button */}
                        <button 
                          onClick={addFoodItem}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '0.8rem 1.4rem',
                            background: '#ffffff',
                            border: '1.5px dashed #10b981',
                            color: '#059669',
                            borderRadius: '12px',
                            cursor: 'pointer',
                            fontWeight: 600,
                            fontSize: '0.92rem',
                            marginTop: '0.5rem',
                            width: '100%',
                            justifyContent: 'center',
                            transition: 'all 0.2s'
                          }}
                        >
                          <Plus size={18} /> Add Missing Food Item (e.g. Salad, Roti, Rice)
                        </button>
                      </div>
                    )}

                    <div style={{ marginTop: '2.5rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                       <button className="btn btn-ghost" onClick={clearFile}>Cancel</button>
                       <button className="btn" onClick={handleFinalCompute} disabled={verificationData.foods.length === 0} style={{ padding: '0.9rem 2rem' }}>Compute Final Nutrition <Sparkles size={18}/></button>
                    </div>
                  </div>
               </motion.div>

            ) : result ? (
              <motion.div key="result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
                
                <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-light)' }}>
                  <div>
                    <h2 style={{ fontSize: '2.4rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-main)' }}>
                      IFCT Analysis Complete <CheckCircle color="var(--primary)" size={32} />
                    </h2>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '0.4rem', flexWrap: 'wrap' }}>
                      <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', margin: 0 }}>Found {result?.detectedFoods?.length || 0} distinct items in your meal plan.</p>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '3px 12px',
                        borderRadius: '20px',
                        fontSize: '0.85rem',
                        fontWeight: 700,
                        background: '#ecfdf5',
                        border: '1.5px solid #a7f3d0',
                        color: '#065f46',
                        textTransform: 'capitalize'
                      }}>
                        {result?.mealType === 'breakfast' && '🍳 Breakfast Context (350–500 kcal)'}
                        {result?.mealType === 'lunch' && '🍛 Lunch Context (550–750 kcal)'}
                        {result?.mealType === 'dinner' && '🌙 Dinner Context (400–550 kcal)'}
                        {result?.mealType === 'snack' && '☕ Snack Context (120–250 kcal)'}
                        {!['breakfast','lunch','dinner','snack'].includes(result?.mealType) && `🍽️ ${result?.mealType || 'Meal'}`}
                      </span>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', background: 'var(--surface-base)', padding: '1rem 1.5rem', borderRadius: '16px', border: '1px solid var(--border-light)', boxShadow: 'var(--shadow-sm)' }}>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '6px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>NutriPlate Score</p>
                    <div style={{ fontSize: '3rem', fontWeight: 900, color: result.score >= 80 ? 'var(--primary)' : 'var(--text-main)', lineHeight: 1 }}>
                      {result?.score || 0}<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)', fontWeight: 600 }}>/100</span>
                    </div>
                  </div>
                </header>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
                    
                    <div className="glass-panel" style={{ padding: '1.5rem' }}>
                      <h4 style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.2rem', fontWeight: 600, fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}><ImageIcon size={18}/> Detected Foods</h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                        {(!result.detectedFoods || result.detectedFoods.length === 0) ? <span style={{ color: 'var(--text-muted)' }}>Processing uncertain...</span> : result.detectedFoods.map((f, i) => (
                          <span key={i} style={{ padding: '8px 14px', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', fontSize: '0.95rem', fontWeight: 600, color: '#1d4ed8', textTransform: 'capitalize' }}>
                            {f.portion > 1 ? `${f.portion}x ` : ''}
                            {f.name?.replace ? f.name.replace('_', ' ') : f.name}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="glass-panel" style={{ padding: '1.5rem' }}>
                      <h4 style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.2rem', fontWeight: 600, fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}><Flame size={18}/> Total Calories</h4>
                      <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--text-main)', lineHeight: 1 }}>
                        {result?.nutrition?.calories || 0} <span style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-muted)' }}>kcal</span>
                      </div>
                    </div>

                    <div className="glass-panel" style={{ padding: '1.5rem' }}>
                      <h4 style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.2rem', fontWeight: 600, fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}><Zap size={18} color="#f59e0b"/> Bioavailable Iron</h4>
                      <div style={{ fontSize: '3rem', fontWeight: 800, color: '#0f766e', lineHeight: 1 }}>
                        {result?.bioavailability?.bioavailableIron !== undefined ? result.bioavailability.bioavailableIron : (result?.nutrition?.iron || 0)} <span style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-muted)' }}>mg</span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px', margin: 0 }}>
                        Gross: <strong>{result?.bioavailability?.grossIron || result?.nutrition?.iron || 0} mg</strong> ({result?.bioavailability?.ironBioavailabilityPct || 8}% absorbed)
                      </p>
                    </div>

                    <div className="glass-panel" style={{ padding: '1.5rem' }}>
                      <h4 style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.2rem', fontWeight: 600, fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}><Activity size={18} color="var(--primary)"/> Absorption Status</h4>
                      <div style={{ marginTop: '4px' }}>
                        <span style={{
                          display: 'inline-block',
                          padding: '6px 14px',
                          borderRadius: '20px',
                          fontSize: '0.9rem',
                          fontWeight: 700,
                          background: result?.bioavailability?.absorptionBadgeColor === '#059669' ? '#ecfdf5' : (result?.bioavailability?.absorptionBadgeColor === '#dc2626' ? '#fef2f2' : '#eff6ff'),
                          color: result?.bioavailability?.absorptionBadgeColor || '#2563eb',
                          border: `1.5px solid ${result?.bioavailability?.absorptionBadgeColor || '#93c5fd'}`
                        }}>
                          ● {result?.bioavailability?.absorptionRating || 'Moderate Absorption'}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '8px', margin: 0 }}>
                        Vit C: <strong>{result?.bioavailability?.vitaminC || 0}mg</strong> • Phytates: <strong>{result?.bioavailability?.phytates || 0}mg</strong>
                      </p>
                    </div>
                </div>

                {/* Charts Section */}
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 1.5fr', gap: '2rem', marginBottom: '2.5rem' }}>
                  
                  <div className="glass-panel" style={{ padding: '2rem', height: '360px' }}>
                     <h4 style={{ color: 'var(--text-main)', marginBottom: '1.5rem', fontWeight: 700, fontSize: '1.1rem' }}>Macro Distribution</h4>
                     <ResponsiveContainer width="100%" height="85%">
                      <PieChart>
                        <Pie 
                          data={[
                            { name: 'Protein (g)', value: result?.nutrition?.protein || 0 },
                            { name: 'Carbs (g)', value: result?.nutrition?.carbs || 0 },
                            { name: 'Fats (g)', value: result?.nutrition?.fat || 0 },
                          ]}
                          cx="50%" cy="50%" innerRadius={75} outerRadius={95} paddingAngle={3} dataKey="value" stroke="none"
                        >
                          {[0,1,2].map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index]} />)}
                        </Pie>
                        <Tooltip />
                        <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '0.9rem', color: 'var(--text-main)', fontWeight: 500 }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="glass-panel" style={{ padding: '2rem', height: '360px' }}>
                    <h4 style={{ color: 'var(--text-main)', marginBottom: '1.5rem', fontWeight: 700, fontSize: '1.1rem' }}>Nutritional Breakdown</h4>
                    <ResponsiveContainer width="100%" height="85%">
                      <BarChart data={[
                        { name: 'Protein', amount: result?.nutrition?.protein || 0, fill: COLORS[0] },
                        { name: 'Carbs', amount: result?.nutrition?.carbs || 0, fill: COLORS[1] },
                        { name: 'Fats', amount: result?.nutrition?.fat || 0, fill: COLORS[2] }
                      ]} layout="vertical" margin={{ top: 0, right: 30, left: 10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                        <XAxis type="number" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis dataKey="name" type="category" stroke="var(--text-main)" fontSize={13} fontWeight={600} tickLine={false} axisLine={false} />
                        <Tooltip cursor={{fill: '#f8fafc'}} />
                        <Bar dataKey="amount" radius={[0, 6, 6, 0]} barSize={28}>
                          {[0,1,2].map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index]} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                </div>

                {/* Biochemical Synergy & Bioavailability Intelligence Panel */}
                <div className="glass-panel" style={{ padding: '2rem', marginTop: '2.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
                    <div>
                      <h3 style={{ fontSize: '1.3rem', display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-main)', margin: 0, fontWeight: 800 }}>
                        <Zap size={22} color="#f59e0b" /> Biochemical Synergy & Nutrient Bioavailability
                      </h3>
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '4px', margin: 0 }}>
                        Models non-heme iron and zinc absorption kinetics modulated by Vitamin C promoters and phytate/tannin chelating inhibitors (ICMR-NIN IFCT 2017).
                      </p>
                    </div>
                    <span style={{
                      padding: '6px 16px',
                      borderRadius: '20px',
                      fontSize: '0.88rem',
                      fontWeight: 700,
                      background: result?.bioavailability?.absorptionBadgeColor === '#059669' ? '#ecfdf5' : (result?.bioavailability?.absorptionBadgeColor === '#dc2626' ? '#fef2f2' : '#eff6ff'),
                      color: result?.bioavailability?.absorptionBadgeColor || '#2563eb',
                      border: `1.5px solid ${result?.bioavailability?.absorptionBadgeColor || '#93c5fd'}`
                    }}>
                      ● {result?.bioavailability?.absorptionRating || 'Moderate Absorption'}
                    </span>
                  </div>

                  {/* 4 Cards: Iron, Zinc, Promoters, Chelators */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '1.2rem', marginBottom: '1.5rem' }}>
                    
                    {/* Card 1: Iron Bioavailability */}
                    <div style={{ padding: '1.2rem', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Bioavailable Iron (Fe)</span>
                        <span style={{ fontSize: '0.78rem', padding: '2px 8px', borderRadius: '12px', background: '#e0f2fe', color: '#0369a1', fontWeight: 600 }}>
                          {result?.bioavailability?.ironBioavailabilityPct || 8}% Absorbed
                        </span>
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f766e', lineHeight: 1 }}>
                        {result?.bioavailability?.bioavailableIron !== undefined ? result.bioavailability.bioavailableIron : (result?.nutrition?.iron || 0)} <span style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-muted)' }}>mg</span>
                      </div>
                      <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                        Gross intake: <strong>{result?.bioavailability?.grossIron || result?.nutrition?.iron || 0} mg</strong> (Non-heme plant iron)
                      </div>
                      <div style={{ marginTop: '10px', height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${Math.min(100, (result?.bioavailability?.ironBioavailabilityPct || 8) * 4)}%`, background: (result?.bioavailability?.ironBioavailabilityPct || 8) >= 12 ? '#059669' : '#f59e0b', borderRadius: '3px' }} />
                      </div>
                    </div>

                    {/* Card 2: Zinc Bioavailability */}
                    <div style={{ padding: '1.2rem', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Bioavailable Zinc (Zn)</span>
                        <span style={{ fontSize: '0.78rem', padding: '2px 8px', borderRadius: '12px', background: '#e0f2fe', color: '#0369a1', fontWeight: 600 }}>
                          {result?.bioavailability?.zincBioavailabilityPct || 15}% Absorbed
                        </span>
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 800, color: '#1d4ed8', lineHeight: 1 }}>
                        {result?.bioavailability?.bioavailableZinc !== undefined ? result.bioavailability.bioavailableZinc : (result?.nutrition?.zinc || 0)} <span style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-muted)' }}>mg</span>
                      </div>
                      <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                        Gross intake: <strong>{result?.bioavailability?.grossZinc || result?.nutrition?.zinc || 0} mg</strong> (Immune enzyme cofactor)
                      </div>
                      <div style={{ marginTop: '10px', height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${Math.min(100, (result?.bioavailability?.zincBioavailabilityPct || 15) * 3)}%`, background: '#3b82f6', borderRadius: '3px' }} />
                      </div>
                    </div>

                    {/* Card 3: Enhancer (Vitamin C) */}
                    <div style={{ padding: '1.2rem', background: '#f0fdf4', borderRadius: '12px', border: '1px solid #bbf7d0' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#166534', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Promoter (Ascorbic Acid)</span>
                        <Leaf size={16} color="#16a34a" />
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 800, color: '#15803d', lineHeight: 1 }}>
                        {result?.bioavailability?.vitaminC || result?.nutrition?.vitaminC || 0} <span style={{ fontSize: '1rem', fontWeight: 600, color: '#166534' }}>mg</span>
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#166534', marginTop: '8px' }}>
                        Reduces Fe³⁺ to Fe²⁺ • <strong>{result?.bioavailability?.ironMultiplier ? `x${result.bioavailability.ironMultiplier} absorption factor` : 'Baseline'}</strong>
                      </div>
                      <div style={{ marginTop: '10px', fontSize: '0.78rem', color: '#15803d', fontWeight: 600 }}>
                        {(result?.bioavailability?.vitaminC || 0) >= 25 ? '✓ Strong reduction of insoluble iron' : '⚠️ Low Vit C - Add lemon or amla'}
                      </div>
                    </div>

                    {/* Card 4: Inhibitors (Phytates & Tannins) */}
                    <div style={{ padding: '1.2rem', background: (result?.bioavailability?.phytates || 0) > 200 ? '#fef2f2' : '#f8fafc', borderRadius: '12px', border: (result?.bioavailability?.phytates || 0) > 200 ? '1.5px solid #fecaca' : '1px solid #e2e8f0' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#991b1b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Chelator Load</span>
                        <ShieldAlert size={16} color="#dc2626" />
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 800, color: '#991b1b', lineHeight: 1 }}>
                        {result?.bioavailability?.phytates || result?.nutrition?.phytate || 0} <span style={{ fontSize: '1rem', fontWeight: 600, color: '#b91c1c' }}>mg</span>
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#7f1d1d', marginTop: '8px' }}>
                        Phytates: <strong>{result?.bioavailability?.phytates || 0} mg</strong> • Tannins: <strong>{result?.bioavailability?.tannins || 0} mg</strong>
                      </div>
                      <div style={{ marginTop: '10px', fontSize: '0.78rem', color: '#991b1b', fontWeight: 600 }}>
                        Phytate:Fe Molar Ratio: <strong>{result?.bioavailability?.phytateToIronMolarRatio || 0}</strong> {(result?.bioavailability?.phytateToIronMolarRatio || 0) > 1.0 ? '(Inhibitory > 1.0)' : '(Optimal < 1.0)'}
                      </div>
                    </div>

                  </div>

                  {/* Synergy Insights List */}
                  {result?.bioavailability?.synergyInsights && result.bioavailability.synergyInsights.length > 0 && (
                    <div style={{ background: '#f8fafc', padding: '1.2rem', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                      <h5 style={{ margin: '0 0 0.8rem 0', fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Sparkles size={16} color="var(--primary)" /> Smart Biochemical Food-Pairing Guidance
                      </h5>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {result.bioavailability.synergyInsights.map((insight, idx) => (
                          <div key={idx} style={{ fontSize: '0.92rem', color: '#334155', lineHeight: 1.5, display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                            <span style={{ color: 'var(--primary)', fontWeight: 800 }}>•</span>
                            <span>{insight}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Antagonistic "Fishy" Nutrient Conflicts Warning Panel */}
                  {result?.bioavailability?.antagonisticCombinations && result.bioavailability.antagonisticCombinations.length > 0 && (
                    <div style={{
                      background: '#fff1f2',
                      border: '1.5px solid #fecdd3',
                      borderRadius: '14px',
                      padding: '1.4rem',
                      marginTop: '1.5rem'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginBottom: '0.6rem' }}>
                        <h4 style={{ margin: 0, color: '#9f1239', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1.05rem', fontWeight: 800 }}>
                          <ShieldAlert size={20} color="#e11d48" /> Conflicting Food Combinations Detected (Absorption Blocked)
                        </h4>
                        <span style={{ fontSize: '0.78rem', background: '#ffe4e6', color: '#be123c', padding: '3px 10px', borderRadius: '12px', fontWeight: 700 }}>
                          {result.bioavailability.antagonisticCombinations.length} Conflict{result.bioavailability.antagonisticCombinations.length > 1 ? 's' : ''} Flagged
                        </span>
                      </div>
                      <p style={{ margin: '0 0 1rem 0', fontSize: '0.86rem', color: '#881337', lineHeight: 1.45 }}>
                        Certain food components eaten together competitively block mucosal uptake or precipitate minerals out of solution before intestinal absorption.
                      </p>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {result.bioavailability.antagonisticCombinations.map((conflict, idx) => (
                          <div key={idx} style={{
                            background: '#ffffff',
                            borderRadius: '10px',
                            border: '1px solid #ffe4e6',
                            padding: '1rem 1.2rem',
                            boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '6px' }}>
                              <span style={{ fontWeight: 800, fontSize: '0.95rem', color: '#be123c' }}>
                                {conflict.title}
                              </span>
                              <span style={{
                                fontSize: '0.75rem',
                                fontWeight: 700,
                                padding: '2px 8px',
                                borderRadius: '12px',
                                background: conflict.severity === 'High' ? '#ffe4e6' : '#fef3c7',
                                color: conflict.severity === 'High' ? '#e11d48' : '#b45309'
                              }}>
                                {conflict.severity} Impact
                              </span>
                            </div>

                            {conflict.dishesInvolved && conflict.dishesInvolved.length > 0 && (
                              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', margin: '6px 0 8px 0', alignItems: 'center' }}>
                                <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 600 }}>Conflicting items on plate:</span>
                                {conflict.dishesInvolved.map((d, dIdx) => (
                                  <span key={dIdx} style={{ fontSize: '0.76rem', background: '#f1f5f9', color: '#334155', padding: '1px 8px', borderRadius: '6px', fontWeight: 600, textTransform: 'capitalize' }}>
                                    {d}
                                  </span>
                                ))}
                              </div>
                            )}

                            <p style={{ margin: '4px 0 6px 0', fontSize: '0.85rem', color: '#334155', lineHeight: 1.45 }}>
                              {conflict.explanation}
                            </p>
                            <div style={{ fontSize: '0.8rem', color: '#64748b', background: '#f8fafc', padding: '6px 10px', borderRadius: '6px', marginBottom: '8px', borderLeft: '3px solid #cbd5e1' }}>
                              🔬 <strong>Biochemical Cause:</strong> {conflict.scientificDetail}
                            </div>
                            <div style={{ fontSize: '0.84rem', color: '#047857', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '5px' }}>
                              <span>💡 Practical Solution:</span> <span>{conflict.solution}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Actionable "What to Add to Maximize Absorption" Boosters */}
                  {result?.bioavailability?.actionableBoosters && result.bioavailability.actionableBoosters.length > 0 && (
                    <div style={{ marginTop: '1.8rem' }}>
                      <div style={{ marginBottom: '1.2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '8px' }}>
                        <div>
                          <h4 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '1.35rem' }}>🚀</span> What to Pair for Maximum Absorption (Culinary Synergy Brain)
                          </h4>
                          <p style={{ margin: '4px 0 0 0', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                            Dish-specific biochemical intelligence (ICMR-NIN IFCT 2017) to unlock the exact nutrients present in your plate (Calcium, Iron, Vitamins, Complete Protein).
                          </p>
                        </div>
                        <span style={{ fontSize: '0.76rem', background: '#ecfdf5', color: '#047857', border: '1px solid #a7f3d0', padding: '4px 10px', borderRadius: '12px', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          ⚡ {result.bioavailability.actionableBoosters.length} Synergy Boosters Available
                        </span>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: '1.3rem' }}>
                        {result.bioavailability.actionableBoosters.map((booster, bIdx) => (
                          <motion.div 
                            key={booster.id || bIdx}
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.35, delay: bIdx * 0.08 }}
                            whileHover={{ 
                              y: -6, 
                              boxShadow: '0 16px 28px -6px rgba(16, 185, 129, 0.14), 0 8px 16px -4px rgba(0, 0, 0, 0.06)',
                              borderColor: '#10b981'
                            }}
                            style={{
                              background: '#ffffff',
                              borderRadius: '16px',
                              border: '1.5px solid #e2e8f0',
                              padding: '1.35rem',
                              display: 'flex',
                              flexDirection: 'column',
                              justifyContent: 'space-between',
                              boxShadow: '0 4px 10px -2px rgba(0,0,0,0.05)',
                              transition: 'border-color 0.25s ease, box-shadow 0.25s ease',
                              position: 'relative'
                            }}
                          >
                            <div>
                              {/* Top Bar: Icon Avatar & Synergy Pill */}
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', gap: '10px' }}>
                                <motion.div 
                                  whileHover={{ rotate: [0, -10, 10, -5, 0], scale: 1.15 }}
                                  transition={{ duration: 0.4 }}
                                  style={{
                                    width: '46px',
                                    height: '46px',
                                    borderRadius: '12px',
                                    background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                                    border: '1.5px solid #bbf7d0',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '1.65rem',
                                    boxShadow: '0 2px 6px rgba(16,185,129,0.12)',
                                    flexShrink: 0,
                                    cursor: 'default'
                                  }}
                                >
                                  {booster.icon}
                                </motion.div>

                                <span style={{
                                  background: 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)',
                                  color: '#14532d',
                                  fontWeight: 800,
                                  fontSize: '0.76rem',
                                  padding: '5px 12px',
                                  borderRadius: '20px',
                                  border: '1px solid #86efac',
                                  boxShadow: '0 2px 5px rgba(22,163,74,0.08)',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                  textAlign: 'right'
                                }}>
                                  <span style={{ display: 'inline-block', animation: 'pulseSubtle 2s infinite' }}>⚡</span>
                                  {booster.synergyEffect || (booster.percentageIncrease ? `+${booster.percentageIncrease}% Boost` : 'Optimal Synergy')}
                                </span>
                              </div>

                              {/* Title & Portion Measure (Full Width - Solves the vertical squeeze bug) */}
                              <div style={{ marginBottom: '12px' }}>
                                <h5 style={{ 
                                  margin: 0, 
                                  fontWeight: 800, 
                                  fontSize: '1.05rem', 
                                  color: '#0f172a', 
                                  lineHeight: 1.35,
                                  letterSpacing: '-0.01em'
                                }}>
                                  {booster.name}
                                </h5>
                                <div style={{ 
                                  display: 'inline-flex', 
                                  alignItems: 'center', 
                                  gap: '4px', 
                                  fontSize: '0.78rem', 
                                  color: '#64748b', 
                                  background: '#f1f5f9', 
                                  padding: '3px 8px', 
                                  borderRadius: '6px', 
                                  marginTop: '6px', 
                                  fontWeight: 600 
                                }}>
                                  <span>📏 Portion:</span> {booster.measure}
                                </div>
                              </div>

                              {/* Detailed Biochemical Breakdown Box */}
                              <div style={{ 
                                background: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)', 
                                padding: '12px', 
                                borderRadius: '12px', 
                                margin: '10px 0', 
                                fontSize: '0.82rem', 
                                border: '1px solid #e2e8f0',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '6px'
                              }}>
                                <div style={{ fontWeight: 800, color: '#0f766e', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                  <span>🎯 Focus:</span> <span style={{ color: '#134e4a' }}>{booster.targetNutrient || 'Nutrient Optimization'}</span>
                                </div>
                                <div style={{ color: '#334155', fontSize: '0.8rem', lineHeight: 1.4 }}>
                                  <strong>Key Catalyst:</strong> {booster.addedNutrient}
                                </div>
                                {booster.projectedBioavailableIron && (
                                  <div style={{ 
                                    color: '#047857', 
                                    fontSize: '0.8rem', 
                                    fontWeight: 700, 
                                    background: '#ecfdf5', 
                                    padding: '4px 8px', 
                                    borderRadius: '6px', 
                                    border: '1px solid #a7f3d0',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '4px'
                                  }}>
                                    ✨ Projected Bioavailable Iron: <strong>{booster.projectedBioavailableIron} mg</strong> ({booster.projectedAbsorptionPct}% absorbed)
                                  </div>
                                )}
                                {booster.culinaryFit && (
                                  <div style={{ color: '#b45309', fontSize: '0.78rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <span>🍽️ Authentic Pairing:</span> {booster.culinaryFit}
                                  </div>
                                )}
                              </div>

                              {/* Why It Works text */}
                              <p style={{ fontSize: '0.84rem', color: '#475569', lineHeight: 1.48, margin: '8px 0 0 0' }}>
                                {booster.whyItWorks}
                              </p>
                            </div>

                            {/* Quick Tip Footer */}
                            <div style={{ 
                              marginTop: '14px', 
                              paddingTop: '10px', 
                              borderTop: '1px dashed #cbd5e1', 
                              fontSize: '0.8rem', 
                              color: '#065f46', 
                              fontWeight: 600,
                              display: 'flex',
                              alignItems: 'flex-start',
                              gap: '6px'
                            }}>
                              <span style={{ fontSize: '1rem', flexShrink: 0 }}>💡</span>
                              <span style={{ lineHeight: 1.4 }}><strong style={{ color: '#047857' }}>Quick Tip:</strong> {booster.quickTip}</span>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="glass-panel" style={{ padding: '2rem', marginTop: '2.5rem' }}>
                  <h3 style={{ marginBottom: '1.5rem', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-main)' }}>
                    <Activity size={20} color="var(--primary)" /> NutriPlate Score Breakdown (ICMR-NIN DGI 2024 Standards)
                  </h3>
                  <div style={{ background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
                    {(!result.scoreBreakdown || result.scoreBreakdown.length === 0) ? (
                      <div style={{ padding: '1.5rem', color: 'var(--text-muted)', textAlign: 'center' }}>Breakdown data not available for this legacy meal.</div>
                    ) : (
                      <>
                        {result.scoreBreakdown.map((item, index) => (
                          <div key={index} style={{ padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', borderBottom: index === result.scoreBreakdown.length - 1 ? 'none' : '1px solid #e2e8f0', background: item.modifier < 0 ? '#fef2f2' : (item.modifier > 0 ? '#ecfdf5' : '#ffffff') }}>
                            <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>{item.factor}</span>
                            <span style={{ fontWeight: 800, color: item.modifier > 0 ? '#059669' : (item.modifier < 0 ? '#dc2626' : 'var(--text-main)') }}>
                               {item.modifier > 0 ? `+${item.modifier}` : item.modifier}
                            </span>
                          </div>
                        ))}
                        <div style={{ padding: '1.2rem 1.5rem', display: 'flex', justifyContent: 'space-between', background: '#f1f5f9', borderTop: '2px solid #e2e8f0' }}>
                           <span style={{ color: 'var(--text-main)', fontWeight: 800 }}>Final Computed Score</span>
                           <span style={{ fontSize: '1.2rem', fontWeight: 900, color: 'var(--primary)' }}>{result.score} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/ 100</span></span>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                <div className="glass-panel" style={{ padding: '2rem', marginTop: '2.5rem' }}>
                  <h3 style={{ marginBottom: '1.5rem', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-main)' }}>
                    <Sparkles size={20} color="var(--primary)" /> Dietary Recommendations
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.2rem' }}>
                    {(!result.recommendations || result.recommendations.length === 0) ? <span style={{ color: 'var(--text-muted)' }}>No AI recommendations generated.</span> : result.recommendations.map((rec, i) => (
                      <div key={i} style={{ padding: '1.2rem', background: '#f8fafc', borderLeft: '4px solid var(--primary)', borderRadius: '0 8px 8px 0', fontSize: '1rem', lineHeight: 1.6, color: 'var(--text-main)', borderTop: '1px solid #e2e8f0', borderRight: '1px solid #e2e8f0', borderBottom: '1px solid #e2e8f0' }}>
                        {rec}
                      </div>
                    ))}
                  </div>
                </div>

              </motion.div>
            ) : (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ height: '100%', minHeight: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                 <div style={{ padding: '2.5rem', background: '#f1f5f9', borderRadius: '50%', marginBottom: '1.5rem' }}>
                   <ImageIcon size={64} strokeWidth={1} color="#94a3b8" />
                 </div>
                 <h2 style={{ fontWeight: 600, fontSize: '1.8rem', color: 'var(--text-main)' }}>Awaiting Meal Upload</h2>
                 <p style={{ color: 'var(--text-muted)', marginTop: '0.8rem', fontSize: '1.1rem' }}>Select an Indian dish to begin the 2-step verification process.</p>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
