const mongoose = require('mongoose');

// User Schema
const userSchema = new mongoose.Schema({
    name: String,
    email: { type: String, unique: true },
    role: { type: String, default: 'basicuser' },
    status: { type: String, enum: ['active', 'inactive'], default: 'active' }
});

const User = mongoose.model('User', userSchema);
module.exports = User;
