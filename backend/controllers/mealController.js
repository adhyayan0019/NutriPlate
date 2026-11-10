const Meal = require('../models/Meal');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');
const nutritionData = require('../utils/nutritionData');
const { getOrFetchNutrition, customDb, loadCustomDb } = require('../utils/aiNutritionFetcher');
const { computeMealBioavailability } = require('../utils/bioavailabilityCalculator');

const FASTAPI_URL = 'http://localhost:8000/predict';

// STEP 1: Process Image, ask AI for predictions, return to User for Verification
const analyzeImage = async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ message: 'Please upload an image' });
        }

        const rawImagePath = path.join(__dirname, '../../uploads', req.file.filename);
        const imagePath = `/uploads/${req.file.filename}`;
        const isVeg = req.body.isVeg !== 'false' && req.body.isVeg !== false;
        
        let initialFoods = [];
        let confidenceLevel = "Low";

        try {
            const formData = new FormData();
            formData.append('file', fs.createReadStream(rawImagePath));
            formData.append('is_veg', isVeg ? 'true' : 'false');

            const aiResponse = await axios.post(FASTAPI_URL, formData, {
                headers: { ...formData.getHeaders() }
            });

            const separatedFoods = aiResponse.data.separated_foods || [];
            const predictions = aiResponse.data.predictions || [];

            if (separatedFoods.length > 0) {
                confidenceLevel = "High (YOLOv8x-seg)";
                const dbKeys = Object.keys(nutritionData);

                separatedFoods.forEach(item => {
                    const cleanLabel = item.name.toLowerCase().replace(/_/g, ' ').trim();
                    let matchedKey = dbKeys.find(k => k === cleanLabel);

                    if (!matchedKey) {
                        matchedKey = dbKeys.find(k => cleanLabel.includes(k) || k.includes(cleanLabel));
                    }

                    const fallbackMeasure = `${item.count > 1 ? item.count + ' Items' : 'Serving'}`;
                    const finalKey = matchedKey || cleanLabel;
                    const measureStr = nutritionData[finalKey]?.measure || fallbackMeasure;

                    initialFoods.push({
                        name: finalKey,
                        originalPrediction: cleanLabel,
                        portion: item.portion || 1.0,
                        count: item.count || 1,
                        confidence: item.confidence,
                        measure: measureStr,
                        box: item.box || null,
                        polygon: item.polygon || [],
                        areaRatio: item.area_ratio || 0,
                        imageSize: item.image_size || null,
                        needsReview: item.needs_review || false
                    });
                });
            } else if (predictions.length > 0) {
                predictions.sort((a, b) => b.confidence - a.confidence);

                if (predictions[0].confidence > 80) confidenceLevel = "High";
                else if (predictions[0].confidence > 50) confidenceLevel = "Medium";

                predictions.forEach(p => {
                    if (p.confidence > 15) {
                        const cleanLabel = p.label.toLowerCase().replace(/_/g, ' ');
                        const dbKeys = Object.keys(nutritionData);
                        let matchedKey = dbKeys.find(k => k === cleanLabel);
                        
                        if (!matchedKey) {
                            matchedKey = dbKeys.find(k => cleanLabel.includes(k) || k.includes(cleanLabel));
                        }

                        if (matchedKey && !initialFoods.some(f => f.name === matchedKey)) {
                            initialFoods.push({
                                name: matchedKey,
                                portion: p.portion || 1.0,
                                count: p.count || 1,
                                confidence: p.confidence,
                                measure: nutritionData[matchedKey].measure || 'Serving'
                            });
                        }
                    }
                });

                // Fallback for extreme low confidence
                if (initialFoods.length === 0 && predictions.length > 0) {
                    const fallbackRaw = predictions[0].label.toLowerCase().replace(/_/g, ' ');
                    const dbKeys = Object.keys(nutritionData);
                    const matchedFallbackKey = dbKeys.find(k => fallbackRaw.includes(k) || k.includes(fallbackRaw));
                    if (matchedFallbackKey) {
                        initialFoods.push({
                            name: matchedFallbackKey,
                            portion: 1.0,
                            count: 1,
                            confidence: predictions[0].confidence,
                            measure: nutritionData[matchedFallbackKey].measure || 'Serving'
                        });
                    }
                }
            }

        } catch (aiError) {
            console.warn("FastAPI AI Model failed. Falling back to mock.");
            const { detectFood } = require('../utils/mockAI');
            const detectedStrings = detectFood(imagePath);
            initialFoods = detectedStrings.map(f => ({
                name: f,
                portion: 1.0,
                measure: nutritionData[f]?.measure || 'Serving'
            }));
            confidenceLevel = "Mock";
        }

        res.status(200).json({
            message: 'Image analyzed, awaiting verification',
            imagePath,
            suggestedFoods: initialFoods,
            confidenceLevel,
            isSegmented: confidenceLevel.includes('YOLOv8x')
        });

    } catch (error) {
        console.error('Analyze image error:', error);
        res.status(500).json({ message: 'Server error while processing image.' });
    }
};

// STEP 2: Receive verified portions, calculate final NIN nutrition, save to DB
const calculateNutrition = async (req, res) => {
    try {
        const { imagePath, mealType, foods } = req.body;
        
        if (!foods || !Array.isArray(foods)) {
            return res.status(400).json({ message: 'Verified foods array is required.' });
        }

        let totalNutrition = { calories: 0, protein: 0, carbs: 0, fat: 0 };
        const confirmedFoods = [];
        
        // 1. Dynamic IFCT AI/Heuristic Mapping & Portion Multiplication
        for (const foodItem of foods) {
            const cleanName = (foodItem.name || '').toLowerCase().trim();
            const exactData = await getOrFetchNutrition(cleanName);
            const multiplier = parseFloat(foodItem.portion) || 1.0;
            
            if (exactData) {
                totalNutrition.calories += (exactData.calories * multiplier);
                totalNutrition.protein += (exactData.protein * multiplier);
                totalNutrition.carbs += (exactData.carbs * multiplier);
                totalNutrition.fat += (exactData.fat * multiplier);
                
                confirmedFoods.push({
                    name: foodItem.name,
                    portion: multiplier,
                    measure: exactData.measure
                });
            }
        }

        // 1b. Compute Biochemical Bioavailability (Iron, Zinc, Phytates, Tannins, Vit C)
        const bioavailability = computeMealBioavailability(confirmedFoods);

        // Ensure 1 decimal point precision max
        totalNutrition = {
            calories: Math.round(totalNutrition.calories),
            protein: Math.round(totalNutrition.protein * 10) / 10,
            carbs: Math.round(totalNutrition.carbs * 10) / 10,
            fat: Math.round(totalNutrition.fat * 10) / 10,
            iron: bioavailability.grossIron,
            zinc: bioavailability.grossZinc,
            vitaminC: bioavailability.vitaminC,
            calcium: bioavailability.calcium,
            phytate: bioavailability.phytates,
            tannin: bioavailability.tannins
        };

        // 2. ICMR-NIN DGI 2024 Calibrated Evaluation Engine by Meal Context
        const MEAL_PROFILES = {
            breakfast: {
                label: 'Breakfast',
                targetMin: 350,
                targetMax: 500,
                hardMin: 200,
                hardMax: 600,
                carbMaxPct: 65,
                fatMaxPct: 32,
                idealShare: '20-25% of daily energy (~400-500 kcal)'
            },
            lunch: {
                label: 'Lunch',
                targetMin: 550,
                targetMax: 750,
                hardMin: 350,
                hardMax: 850,
                carbMaxPct: 60,
                fatMaxPct: 30,
                idealShare: '30-35% of daily energy (~600-750 kcal)'
            },
            dinner: {
                label: 'Dinner',
                targetMin: 400,
                targetMax: 550,
                hardMin: 250,
                hardMax: 650,
                carbMaxPct: 58, // Stricter nocturnal carb ceiling as per ICMR-NIN 2024
                fatMaxPct: 28,
                idealShare: '20-25% of daily energy (~450-550 kcal)'
            },
            snack: {
                label: 'Snack',
                targetMin: 120,
                targetMax: 250,
                hardMin: 50,
                hardMax: 300,
                carbMaxPct: 65,
                fatMaxPct: 35,
                idealShare: '10% of daily energy (~150-250 kcal)'
            }
        };

        const currentMealKey = (mealType || 'lunch').toLowerCase().trim();
        const profile = MEAL_PROFILES[currentMealKey] || MEAL_PROFILES.lunch;

        let score = 100;
        const recommendations = [];
        const scoreBreakdown = [];
        
        scoreBreakdown.push({ factor: `Initial DGI Baseline (${profile.label})`, modifier: 100 });

        // Caloric Rules (ICMR-NIN 2024 energy limits calibrated for each meal context)
        if (totalNutrition.calories > profile.hardMax) {
            const overage = totalNutrition.calories - profile.targetMax;
            const penalty = Math.min(45, Math.max(10, Math.ceil(overage / 60) * 6));
            score -= penalty;
            scoreBreakdown.push({ factor: `${profile.label} Caloric Surplus (+${Math.round(overage)} kcal over target)`, modifier: -penalty });
            
            if (currentMealKey === 'snack') {
                recommendations.push(`Snack caloric overload (${totalNutrition.calories} kcal vs ~200 kcal budget). DGI 2024 warns heavy snacking leads to silent weight gain. Choose roasted makhanas, nuts, or fruits.`);
            } else if (currentMealKey === 'dinner') {
                recommendations.push(`High bedtime calories (${totalNutrition.calories} kcal). DGI 2024 advises lighter dinners (< 550 kcal) to prevent nocturnal glucose surges and visceral fat storage.`);
            } else if (currentMealKey === 'breakfast') {
                recommendations.push(`Excessive breakfast calories (${totalNutrition.calories} kcal vs 400-500 kcal target). Moderate portion sizes for sustained morning focus.`);
            } else {
                recommendations.push(`Caloric surplus for ${profile.label} (${totalNutrition.calories} kcal vs ~700 kcal limit). DGI 2024 suggests reducing grain/oil portions.`);
            }
        } else if (totalNutrition.calories < profile.hardMin) {
            score -= 10;
            scoreBreakdown.push({ factor: `${profile.label} Energy Deficit (< ${profile.hardMin} kcal)`, modifier: -10 });
            if (currentMealKey === 'snack') {
                recommendations.push(`Very low snack energy (${totalNutrition.calories} kcal). Add a handful of mixed nuts or a fruit for essential micronutrients.`);
            } else {
                recommendations.push(`${profile.label} is below the ${profile.hardMin} kcal threshold to maintain basal energy requirements.`);
            }
        } else if (totalNutrition.calories >= profile.targetMin && totalNutrition.calories <= profile.targetMax) {
            score += 5;
            scoreBreakdown.push({ factor: `Optimal ${profile.label} Energy (${totalNutrition.calories} kcal)`, modifier: +5 });
            recommendations.push(`Calorie density perfectly matches ICMR-NIN 2024 ${profile.label} energy targets (${profile.targetMin}-${profile.targetMax} kcal).`);
        }

        // PE Ratio (Protein-to-Energy: DGI mandates 10-15% of energy from protein)
        const proteinPct = ((totalNutrition.protein * 4) / (totalNutrition.calories || 1)) * 100;
        
        if (currentMealKey === 'snack') {
            if (proteinPct >= 12) {
                score += 8;
                scoreBreakdown.push({ factor: `High-Protein Smart Snack (${proteinPct.toFixed(1)}% PE ratio)`, modifier: +8 });
                recommendations.push('Superb high-protein snack! Protein-dense snacks (sprouts, chana, paneer, nuts) stabilize daytime blood glucose.');
            } else if (proteinPct < 6 && totalNutrition.calories > 150) {
                score -= 10;
                scoreBreakdown.push({ factor: `Low-Protein Snack (${proteinPct.toFixed(1)}% PE ratio)`, modifier: -10 });
                recommendations.push('Snack is predominantly carbohydrates/fats. Pair with roasted peanuts, sprouts, or roasted chana.');
            }
        } else {
            if (proteinPct < 10) {
                score -= 20;
                scoreBreakdown.push({ factor: `Protein deficit (${proteinPct.toFixed(1)}% of energy, DGI min 10%)`, modifier: -20 });
                recommendations.push('Grossly deficient in protein. DGI 2024 warns against protein-poor diets. Add dal, paneer, curd, or lean protein.');
            } else if (proteinPct >= 12) {
                score += 5;
                scoreBreakdown.push({ factor: 'Optimal PE Ratio (DGI Compliant)', modifier: +5 });
                recommendations.push('Excellent protein-to-energy ratio ensuring proper muscle maintenance.');
            }
        }

        // Carbohydrate Rules (DGI limits)
        const carbPct = ((totalNutrition.carbs * 4) / (totalNutrition.calories || 1)) * 100;
        if (carbPct > profile.carbMaxPct) {
            const carbPenalty = currentMealKey === 'dinner' ? 25 : 20;
            score -= carbPenalty;
            scoreBreakdown.push({ factor: `${profile.label} Carb Overload (${carbPct.toFixed(1)}% of energy, limit ${profile.carbMaxPct}%)`, modifier: -carbPenalty });
            if (currentMealKey === 'dinner') {
                recommendations.push(`Excessive bedtime carbohydrates (${carbPct.toFixed(1)}%). DGI 2024 stresses keeping dinner carbs below 58% to prevent nighttime insulin spikes.`);
            } else {
                recommendations.push(`Dangerous carbohydrate spike (${carbPct.toFixed(1)}%). DGI 2024 restricts meals crossing ${profile.carbMaxPct}% carb energy to prevent metabolic issues.`);
            }
        }

        // Fat Rules (DGI limits)
        const fatPct = ((totalNutrition.fat * 9) / (totalNutrition.calories || 1)) * 100;
        if (fatPct > profile.fatMaxPct) {
            score -= 20;
            scoreBreakdown.push({ factor: `Excess Fat (${fatPct.toFixed(1)}% of energy, limit ${profile.fatMaxPct}%)`, modifier: -20 });
            recommendations.push('High fat concentration! IFCT stats flag this. Switch to steaming or baking instead of deep-frying.');
        }

        // Protective Food Check (Vegetables for main meals, Fruits/Nuts for breakfast/snack)
        const veggieKeywords = ['salad', 'sabzi', 'spinach', 'broccoli', 'palak', 'methi', 'gobi', 'bhindi', 'beans', 'carrot', 'cucumber', 'curry'];
        const snackProtectiveKeywords = ['fruit', 'apple', 'banana', 'papaya', 'orange', 'nuts', 'almond', 'walnut', 'sprout', 'makhana', 'chana', 'salad'];
        
        if (currentMealKey === 'lunch' || currentMealKey === 'dinner') {
            const hasVeggie = confirmedFoods.some(f => veggieKeywords.some(v => f.name.toLowerCase().includes(v)));
            if (!hasVeggie) {
                score -= 10;
                scoreBreakdown.push({ factor: 'Missing protective foods (Veggies)', modifier: -10 });
                recommendations.push('Zero micronutrient sources detected. DGI stresses consuming 400g of vegetables/fruits daily.');
            }
        } else {
            const hasProtective = confirmedFoods.some(f => snackProtectiveKeywords.some(v => f.name.toLowerCase().includes(v)));
            if (hasProtective) {
                score += 5;
                scoreBreakdown.push({ factor: 'Protective Food Source (Fruit/Nuts/Sprouts)', modifier: +5 });
                recommendations.push('Includes beneficial protective foods rich in natural vitamins and antioxidants.');
            }
        }

        // Biochemical Bioavailability Score Adjustment (ICMR-NIN Synergy Bonus/Penalty)
        if (bioavailability.scoreModifier > 0) {
            score += bioavailability.scoreModifier;
            scoreBreakdown.push({
                factor: 'Biochemical Synergy Bonus (Promoter-Enhanced Bioavailability)',
                modifier: bioavailability.scoreModifier
            });
        } else if (bioavailability.scoreModifier < 0) {
            score += bioavailability.scoreModifier;
            scoreBreakdown.push({
                factor: 'Phytate Chelation Penalty (Inhibited Mineral Absorption)',
                modifier: bioavailability.scoreModifier
            });
        }

        // Add actionable synergy recommendations
        if (bioavailability.synergyInsights && bioavailability.synergyInsights.length > 0) {
            recommendations.push(...bioavailability.synergyInsights);
        }

        score = Math.max(10, Math.min(100, Math.round(score)));

        // 3. Save to Database
        const newMeal = new Meal({
            userId: req.user.userId || req.user.id,
            mealType: (mealType || 'lunch').toString().toLowerCase().trim(),
            imagePath: imagePath || '/uploads/sample.jpg',
            detectedFoods: confirmedFoods, // Array of structured objects
            nutrition: totalNutrition,
            bioavailability,
            score,
            scoreBreakdown,
            recommendations
        });

        await newMeal.save();

        // 4. Human-in-the-Loop Active Learning Forwarder
        if (req.body.feedbacks && Array.isArray(req.body.feedbacks) && req.body.feedbacks.length > 0) {
            req.body.feedbacks.forEach(fb => {
                if (fb.original && fb.corrected && fb.original !== fb.corrected) {
                    axios.post('http://localhost:8000/feedback', {
                        original_label: fb.original,
                        corrected_label: fb.corrected,
                        image_path: imagePath || '',
                        meal_type: mealType || 'lunch'
                    }).catch(e => console.warn('HITL feedback forward note:', e.message));
                }
            });
        }

        // 5. Active Learning: Memorize whole plate layout (user drawn boxes, portions, and items)
        if (foods && Array.isArray(foods) && foods.length > 0) {
            axios.post('http://localhost:8000/record-plate', {
                image_path: imagePath || '',
                meal_type: mealType || 'lunch',
                foods: foods
            }).catch(e => console.warn('HITL record-plate forward note:', e.message));
        }

        res.status(201).json({
            message: 'Nutrition calculated and saved',
            meal: newMeal
        });

    } catch (error) {
        console.error('Calculate nutrition error:', error);
        res.status(500).json({ message: 'Server error while evaluating IFCT metrics.' });
    }
};

const submitFeedback = async (req, res) => {
    try {
        const { originalLabel, correctedLabel, imagePath, mealType } = req.body;
        await axios.post('http://localhost:8000/feedback', {
            original_label: originalLabel || '',
            corrected_label: correctedLabel || '',
            image_path: imagePath || '',
            meal_type: mealType || 'lunch'
        });
        res.status(200).json({ message: 'Active learning feedback logged successfully' });
    } catch (err) {
        res.status(200).json({ message: 'Feedback recorded' });
    }
};

const getMeals = async (req, res) => {
    try {
        const meals = await Meal.find({ userId: req.user.userId }).sort({ createdAt: -1 });
        res.status(200).json(meals);
    } catch (error) {
        console.error('Fetch meals error:', error);
        res.status(500).json({ message: 'Server error fetching meal history' });
    }
};

const getFoodNutrition = async (req, res) => {
    try {
        const foodName = req.params.foodName;
        const profile = await getOrFetchNutrition(foodName);
        if (!profile) {
            return res.status(404).json({ message: 'Nutrition profile not found' });
        }
        res.status(200).json({ foodName, nutrition: profile });
    } catch (err) {
        res.status(500).json({ message: 'Error retrieving food nutrition' });
    }
};

const getAllDishes = (req, res) => {
    try {
        if (typeof loadCustomDb === 'function') {
            loadCustomDb();
        }
        const set = new Set([
            ...Object.keys(nutritionData),
            ...Object.keys(customDb || {})
        ]);
        const dishes = Array.from(set).map(d => d.trim()).filter(Boolean).sort();
        res.status(200).json({ dishes, count: dishes.length });
    } catch (err) {
        res.status(500).json({ message: 'Error retrieving dishes list' });
    }
};

module.exports = { analyzeImage, calculateNutrition, getMeals, submitFeedback, getFoodNutrition, getAllDishes };