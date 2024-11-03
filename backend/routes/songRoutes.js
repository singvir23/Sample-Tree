const express = require('express');
const { spawn } = require('child_process');
const Song = require('../models/Song');

const router = express.Router();

router.get('/song/:title', async (req, res) => {
    const title = req.params.title;
    let song = await Song.findOne({ title: title });

    if (!song) {
        // If the song is not found, call the scraper
        const url = `https://www.whosampled.com/${title}/`;

        // Spawn a Python child process to execute the scraper
        const pythonProcess = spawn('python3', ['backend/utils/scraper.py', url]);

        pythonProcess.stdout.on('data', (data) => {
            // Parse the result from Python and save it in the database
            const songData = JSON.parse(data.toString());
            Song.create(songData).then((newSong) => {
                res.json(newSong);
            }).catch(err => res.status(500).json({ error: err.message }));
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`Error: ${data}`);
            res.status(500).json({ error: 'Error occurred while scraping.' });
        });
    } else {
        res.json(song);
    }
});

module.exports = router;
