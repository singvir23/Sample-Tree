const express = require('express');
const Song = require('../models/Song'); // MongoDB schema for songs
const { spawn } = require('child_process');
const router = express.Router();

// Get song data by title
router.get('/song/:title', async (req, res) => {
    const title = req.params.title;

    try {
        // Check if song exists in the MongoDB database
        let song = await Song.findOne({ title: title });

        if (song) {
            // If found, return the song data
            res.json(song);
        } else {
            // If not found, run the Python scraper
            const pythonProcess = spawn('python3', ['backend/utils/scraper.py', `https://www.whosampled.com/${title}/`]);

            pythonProcess.stdout.on('data', async (data) => {
                try {
                    // Parse the data from Python scraper
                    const songData = JSON.parse(data.toString());

                    // Save the new song data to MongoDB
                    const newSong = await Song.create(songData);
                    
                    // Return the newly saved song data to the client
                    res.json(newSong);
                } catch (error) {
                    console.error('Error saving song data:', error);
                    res.status(500).json({ error: 'Error saving scraped song data.' });
                }
            });

            pythonProcess.stderr.on('data', (data) => {
                console.error(`Error from scraper: ${data}`);
                res.status(500).json({ error: 'Error occurred while scraping.' });
            });
        }
    } catch (error) {
        console.error('Error fetching song:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
