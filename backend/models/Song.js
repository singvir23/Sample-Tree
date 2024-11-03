const mongoose = require('mongoose');

const songSchema = new mongoose.Schema({
    title: String,
    artist: String,
    samples: Array,
    sampled_by: Array
});

module.exports = mongoose.model('Song', songSchema);
