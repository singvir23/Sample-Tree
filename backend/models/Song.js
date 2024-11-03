const mongoose = require('mongoose');

const SongSchema = new mongoose.Schema({
    title: String,
    artist: String,
    year: String,
    samples: Array,
    sampled_by: Array
});

module.exports = mongoose.model('Song', SongSchema);
