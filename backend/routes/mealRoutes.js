const express = require('express');
const router = express.Router();
const { analyzeImage, calculateNutrition, getMeals, submitFeedback, getFoodNutrition, getAllDishes } = require('../controllers/mealController');
const { authMiddleware } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

router.post('/analyze-image', authMiddleware, upload.single('image'), analyzeImage);
router.post('/calculate-nutrition', authMiddleware, calculateNutrition);
router.post('/feedback', authMiddleware, submitFeedback);
router.get('/meals', authMiddleware, getMeals);
router.get('/nutrition/:foodName', getFoodNutrition);
router.get('/dishes', getAllDishes);

module.exports = router;
