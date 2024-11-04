// routes/songRoutes.js
const express = require('express');
const router = express.Router();

// GET all songs
router.get('/songs', async (req, res) => {
    try {
        const db = req.app.locals.dbClient.db('your_database_name');
        const songs = await db.collection('songs').find({}).toArray();
        res.json(songs);
    } catch (error) {
        console.error('Error fetching songs:', error);
        res.status(500).json({ error: 'Error fetching songs' });
    }
});

// Add more routes as needed

module.exports = router;