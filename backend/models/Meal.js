const mongoose = require('mongoose');

const MealSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    mealType: {
        type: String,
        enum: ['breakfast', 'lunch', 'dinner', 'snack'],
        lowercase: true,
        required: true
    },
    imagePath: {
        type: String,
        required: true
    },
    detectedFoods: [{
        name: { type: String, required: true },
        portion: { type: Number, default: 1 },
        measure: { type: String, default: '' }
    }],
    nutrition: {
        calories: { type: Number, default: 0 },
        protein: { type: Number, default: 0 },
        carbs: { type: Number, default: 0 },
        fat: { type: Number, default: 0 },
        fiber: { type: Number, default: 0 },
        iron: { type: Number, default: 0 },
        zinc: { type: Number, default: 0 },
        vitaminC: { type: Number, default: 0 },
        calcium: { type: Number, default: 0 },
        phytate: { type: Number, default: 0 },
        tannin: { type: Number, default: 0 }
    },
    bioavailability: {
        grossIron: { type: Number, default: 0 },
        bioavailableIron: { type: Number, default: 0 },
        ironBioavailabilityPct: { type: Number, default: 0 },
        grossZinc: { type: Number, default: 0 },
        bioavailableZinc: { type: Number, default: 0 },
        zincBioavailabilityPct: { type: Number, default: 0 },
        vitaminC: { type: Number, default: 0 },
        phytates: { type: Number, default: 0 },
        tannins: { type: Number, default: 0 },
        calcium: { type: Number, default: 0 },
        phytateToIronMolarRatio: { type: Number, default: 0 },
        phytateToZincMolarRatio: { type: Number, default: 0 },
        ironMultiplier: { type: Number, default: 1.0 },
        absorptionRating: { type: String, default: 'Moderate' },
        absorptionBadgeColor: { type: String, default: '#3b82f6' },
        synergyInsights: [{ type: String }],
        dishBreakdowns: [{
            name: String,
            portion: Number,
            iron: Number,
            zinc: Number,
            vitaminC: Number,
            phytate: Number
        }],
        antagonisticCombinations: [{
            type: { type: String },
            severity: { type: String },
            title: { type: String },
            dishesInvolved: [{ type: String }],
            explanation: { type: String },
            scientificDetail: { type: String },
            solution: { type: String }
        }],
        actionableBoosters: [{
            id: { type: String },
            name: { type: String },
            icon: { type: String },
            targetNutrient: { type: String },
            measure: { type: String },
            addedNutrient: { type: String },
            synergyEffect: { type: String },
            projectedAbsorptionPct: { type: Number },
            projectedBioavailableIron: { type: Number },
            percentageIncrease: { type: Number },
            whyItWorks: { type: String },
            quickTip: { type: String },
            culinaryFit: { type: String }
        }]
    },
    score: {
        type: Number,
        default: 0
    },
    recommendations: [{
        type: String
    }],
    scoreBreakdown: [{
        factor: String,
        modifier: Number
    }]
}, { timestamps: true });

module.exports = mongoose.model('Meal', MealSchema);
