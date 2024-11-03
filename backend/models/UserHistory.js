const mongoose = require('mongoose');

const UserHistorySchema = new mongoose.Schema({
    ip: String,
    timestamp: { type: Date, default: Date.now },
    root_song: Object,
    tree_snapshot: Array
});

module.exports = mongoose.model('UserHistory', UserHistorySchema);
