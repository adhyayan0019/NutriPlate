const nutritionData = require('./nutritionData');

/**
 * Mock Food Detection Model
 * In a real application, this would call a Python microservice 
 * or an external API like Clarifai / Google Vision to analyze the image.
 * Here, we randomly select 2-4 items from our dictionary.
 */
const detectFood = (imagePath) => {
    const foodKeys = Object.keys(nutritionData);
    
    // Pick a random number of items between 2 and 4
    const numItems = Math.floor(Math.random() * 3) + 2; 

    // Shuffle and pick
    const shuffled = foodKeys.sort(() => 0.5 - Math.random());
    const detectedItems = shuffled.slice(0, numItems);

    return detectedItems;
};

module.exports = { detectFood };
