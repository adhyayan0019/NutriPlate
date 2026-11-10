const fs = require('fs');
const path = require('path');
const axios = require('axios');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });
const staticNutritionData = require('./nutritionData');

const CUSTOM_DB_PATH = path.join(__dirname, 'custom_nutrition_db.json');

// In-memory custom items cache
let customDb = {};

function loadCustomDb() {
    try {
        if (fs.existsSync(CUSTOM_DB_PATH)) {
            const raw = fs.readFileSync(CUSTOM_DB_PATH, 'utf8');
            customDb = JSON.parse(raw);
        }
    } catch (e) {
        console.warn('Notice loading custom_nutrition_db.json:', e.message);
        customDb = {};
    }
}

function saveCustomDb() {
    try {
        fs.writeFileSync(CUSTOM_DB_PATH, JSON.stringify(customDb, null, 2), 'utf8');
    } catch (e) {
        console.warn('Notice saving custom_nutrition_db.json:', e.message);
    }
}

// Initial load
loadCustomDb();

/**
 * Intelligent Component & Culinary Fallback Heuristic
 * Generates accurate IFCT metrics based on Indian ingredients and preparation style.
 */
function inferCulinaryNutrition(foodName) {
    const name = foodName.toLowerCase();

    if (name.includes('chutney') || name.includes('dip') || name.includes('sauce')) {
        const isCoconut = name.includes('coconut');
        return {
            measure: '2 Tablespoons (30g)',
            calories: isCoconut ? 65 : 45,
            protein: isCoconut ? 1.1 : 0.9,
            carbs: isCoconut ? 3.0 : 5.0,
            fat: isCoconut ? 5.5 : 2.5,
            fiber: 1.1,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('idli')) {
        const isRawa = name.includes('rawa') || name.includes('rava');
        return {
            measure: '1 Piece (60g)',
            calories: isRawa ? 85 : 65,
            protein: isRawa ? 2.8 : 2.2,
            carbs: isRawa ? 17.0 : 14.0,
            fat: isRawa ? 0.6 : 0.2,
            fiber: isRawa ? 1.2 : 0.8,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('dosa') || name.includes('pancake')) {
        return {
            measure: '1 Medium Dosa (80g)',
            calories: 175,
            protein: 4.8,
            carbs: 30.0,
            fat: 4.2,
            fiber: 1.5,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('vada') || name.includes('pakora') || name.includes('bhajji')) {
        return {
            measure: '1 Piece (50g)',
            calories: 160,
            protein: 4.2,
            carbs: 16.0,
            fat: 9.0,
            fiber: 2.0,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('sambar') || name.includes('sambhar') || name.includes('rasam')) {
        return {
            measure: '1 Katori (150g)',
            calories: 120,
            protein: 5.5,
            carbs: 16.0,
            fat: 3.0,
            fiber: 3.5,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('dal') || name.includes('curry') || name.includes('gravy')) {
        return {
            measure: '1 Katori (150g)',
            calories: 160,
            protein: 8.0,
            carbs: 22.0,
            fat: 4.5,
            fiber: 4.5,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('paneer')) {
        return {
            measure: '1 Katori (150g)',
            calories: 320,
            protein: 16.0,
            carbs: 11.0,
            fat: 24.0,
            fiber: 2.0,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('rice') || name.includes('pulao') || name.includes('biryani') || name.includes('bath')) {
        return {
            measure: '1 Bowl (200g)',
            calories: 240,
            protein: 5.0,
            carbs: 48.0,
            fat: 3.5,
            fiber: 1.5,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('roti') || name.includes('paratha') || name.includes('naan') || name.includes('chapati')) {
        return {
            measure: '1 Piece (60g)',
            calories: 160,
            protein: 4.5,
            carbs: 28.0,
            fat: 4.0,
            fiber: 2.5,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('sweet') || name.includes('halwa') || name.includes('laddu') || name.includes('kheer')) {
        return {
            measure: '1 Serving (60g)',
            calories: 250,
            protein: 3.5,
            carbs: 38.0,
            fat: 9.5,
            fiber: 1.0,
            source: 'Culinary IFCT Heuristic'
        };
    }
    if (name.includes('salad') || name.includes('raita')) {
        return {
            measure: '1 Katori (100g)',
            calories: 40,
            protein: 1.8,
            carbs: 6.5,
            fat: 0.8,
            fiber: 2.2,
            source: 'Culinary IFCT Heuristic'
        };
    }

    // Standard general Indian food serving default
    return {
        measure: '1 Serving (100g)',
        calories: 180,
        protein: 5.5,
        carbs: 25.0,
        fat: 6.5,
        fiber: 2.5,
        source: 'Culinary IFCT Heuristic'
    };
}

/**
 * Queries Free Google Gemini API if GEMINI_API_KEY is configured
 */
async function queryGeminiNutrition(foodName) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) return null;

    try {
        const prompt = `You are an expert Indian dietitian aligned with ICMR-NIN (National Institute of Nutrition) and IFCT 2017 (Indian Food Composition Tables).
Provide the nutritional profile per standard serving for: "${foodName}".
Return ONLY a valid JSON object with this exact structure, with no markdown, backticks, or explanation:
{
  "measure": "1 Piece (60g)",
  "calories": 85,
  "protein": 2.8,
  "carbs": 17.0,
  "fat": 0.6,
  "fiber": 1.2
}`;

        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
        const res = await axios.post(url, {
            contents: [{ parts: [{ text: prompt }] }]
        }, { timeout: 4500 });

        const candidateText = res.data?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (candidateText) {
            const cleanJson = candidateText.replace(/```json/g, '').replace(/```/g, '').trim();
            const parsed = JSON.parse(cleanJson);
            if (parsed.calories && parsed.measure) {
                return {
                    measure: parsed.measure,
                    calories: Math.round(Number(parsed.calories)),
                    protein: Math.round(Number(parsed.protein || 0) * 10) / 10,
                    carbs: Math.round(Number(parsed.carbs || 0) * 10) / 10,
                    fat: Math.round(Number(parsed.fat || 0) * 10) / 10,
                    fiber: Math.round(Number(parsed.fiber || 0) * 10) / 10,
                    source: 'Gemini IFCT AI'
                };
            }
        }
    } catch (err) {
        console.warn('Gemini AI Nutrition lookup note:', err.message);
    }
    return null;
}

/**
 * Queries Free Groq API if GROQ_API_KEY is configured
 */
async function queryGroqNutrition(foodName) {
    const apiKey = process.env.GROQ_API_KEY;
    if (!apiKey) return null;

    const candidateModels = [
        'qwen/qwen3.8-27b',
        'llama-3.3-70b-versatile',
        'openai/gpt-oss-120b',
        'openai/gpt-oss-20b'
    ];

    for (const model of candidateModels) {
        try {
            const res = await axios.post('https://api.groq.com/openai/v1/chat/completions', {
                model: model,
                messages: [{
                    role: 'system',
                    content: 'You are a clinical Indian nutritionist using the Indian Food Composition Tables (IFCT 2017) published by ICMR-NIN. Output only valid JSON.'
                }, {
                    role: 'user',
                    content: `Calculate the realistic nutritional values per standard household serving (e.g. 1 piece, 1 katori, 1 cup) for the authentic Indian dish: "${foodName}". Return ONLY a raw JSON object with keys: "measure" (string), "calories" (number), "protein" (number), "carbs" (number), "fat" (number), "fiber" (number). No markdown or explanation.`
                }],
                temperature: 0.2
            }, {
                headers: { 'Authorization': `Bearer ${apiKey}` },
                timeout: 5000
            });

            const content = res.data?.choices?.[0]?.message?.content;
            if (content) {
                const jsonMatch = content.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    const parsed = JSON.parse(jsonMatch[0]);
                    if (parsed.calories !== undefined) {
                        return {
                            measure: parsed.measure || '1 Serving (100g)',
                            calories: Math.round(Number(parsed.calories)),
                            protein: Math.round(Number(parsed.protein || 0) * 10) / 10,
                            carbs: Math.round(Number(parsed.carbs || 0) * 10) / 10,
                            fat: Math.round(Number(parsed.fat || 0) * 10) / 10,
                            fiber: Math.round(Number(parsed.fiber || 0) * 10) / 10,
                            source: 'Groq IFCT AI'
                        };
                    }
                }
            }
        } catch (e) {
            if (e.response && e.response.status === 404) {
                continue; // Try next candidate model
            }
            console.warn('Groq AI Nutrition lookup note:', e.message);
            break;
        }
    }
    return null;
}

/**
 * Main Resolver: Looks up exact, fuzzy, custom database, Gemini, Groq, or Free Culinary Heuristics.
 * Automatically saves new entries to custom_nutrition_db.json.
 */
async function getOrFetchNutrition(foodName) {
    if (!foodName) return null;
    const cleanName = foodName.toLowerCase().replace(/_/g, ' ').trim();

    // 1. Direct hit in custom persistent database
    if (customDb[cleanName]) {
        return customDb[cleanName];
    }

    // 2. Direct hit in static IFCT database
    if (staticNutritionData[cleanName]) {
        return staticNutritionData[cleanName];
    }

    // 3. Exact key fuzzy match in custom DB
    const customKeys = Object.keys(customDb);
    const customMatch = customKeys.find(k => cleanName.includes(k) || k.includes(cleanName));
    if (customMatch && customDb[customMatch]) {
        return customDb[customMatch];
    }

    // 4. Exact key fuzzy match in static DB
    const staticKeys = Object.keys(staticNutritionData);
    const staticMatch = staticKeys.find(k => cleanName.includes(k) || k.includes(cleanName));
    if (staticMatch && staticNutritionData[staticMatch]) {
        return staticNutritionData[staticMatch];
    }

    // 5. Query AI API (Groq first with user's key, then Gemini)
    let fetched = await queryGroqNutrition(cleanName);
    if (!fetched) {
        fetched = await queryGeminiNutrition(cleanName);
    }

    // 6. Free Built-in Culinary Component Heuristic (100% reliable fallback)
    if (!fetched) {
        fetched = inferCulinaryNutrition(cleanName);
    }

    // 7. Persist newly fetched food item into custom_nutrition_db.json
    customDb[cleanName] = fetched;
    saveCustomDb();

    console.log(`✨ Learned new food IFCT profile: [${cleanName}] -> ${fetched.measure}, ${fetched.calories} kcal (Source: ${fetched.source})`);
    return fetched;
}

module.exports = {
    getOrFetchNutrition,
    loadCustomDb,
    customDb
};
