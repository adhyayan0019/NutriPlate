const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env') });
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const authRoutes = require('./routes/authRoutes');
const mealRoutes = require('./routes/mealRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const fs = require('fs');

// Static directories
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));
const distPath = path.join(__dirname, '../frontend/dist');
if (fs.existsSync(distPath)) {
    app.use(express.static(distPath));
} else {
    app.use(express.static(path.join(__dirname, '../frontend')));
}

// Routes
app.use('/api', authRoutes);
app.use('/api', mealRoutes);

// SPA client-side routing fallback for Express 5
app.use((req, res, next) => {
    if (req.method !== 'GET') return next();
    if (req.path.startsWith('/api') || req.path.startsWith('/uploads')) {
        return next();
    }
    const targetIndex = fs.existsSync(distPath) 
        ? path.join(distPath, 'index.html') 
        : path.join(__dirname, '../frontend/index.html');
    res.sendFile(targetIndex);
});

// Database configuration
// Using a local mongodb database for this college project
const MONGODB_URI = 'mongodb://127.0.0.1:27017/indian_smart_plate';

mongoose.connect(MONGODB_URI)
.then(() => {
    console.log('Connected to MongoDB local instance');
    app.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
    });
})
.catch(err => {
    console.error('Failed to connect to MongoDB', err);
});
