const express = require('express');
const router = express.Router();

// Route to get song data by title
router.get('/song/:title', async (req, res) => {
    const title = req.params.title;

    try {
        const dbClient = req.app.locals.dbClient;
        const db = dbClient.db('whosampled_db'); // Connect to 'whosampled_db' database
        const songCollection = db.collection('Song'); // Connect to 'Song' collection

        // Check if song exists in the MongoDB database
        const song = await songCollection.findOne({ original_song: { $regex: title, $options: 'i' } });

        if (song) {
            // If found, return the song data
            return res.json(song);
        } else {
            // If the song is not found, return a 404 error
            return res.status(404).json({ error: "Song not found" });
        }
    } catch (error) {
        console.error('Error fetching song:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
