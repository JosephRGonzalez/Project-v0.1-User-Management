const express = require('express');
const User = require('../models/userModel');
const router = express.Router();

// Create User
router.post('/', async (req, res) => {
    const { name, email, role } = req.body;
    const newUser = new User({ name, email, role });
    await newUser.save();
    res.status(201).json(newUser);
});

// Get Users
router.get('/', async (req, res) => {
    const users = await User.find();
    res.json(users);
});

// Update User
router.put('/:id', async (req, res) => {
    const updatedUser = await User.findByIdAndUpdate(req.params.id, req.body, { new: true });
    res.json(updatedUser);
});

// Delete User
router.delete('/:id', async (req, res) => {
    await User.findByIdAndDelete(req.params.id);
    res.status(204).send();
});

// Deactivate User
router.put('/deactivate/:id', async (req, res) => {
    const deactivatedUser = await User.findByIdAndUpdate(req.params.id, { status: 'inactive' }, { new: true });
    res.json(deactivatedUser);
});

// Reactivate User
router.put('/reactivate/:id', async (req, res) => {
    const reactivatedUser = await User.findByIdAndUpdate(req.params.id, { status: 'active' }, { new: true });
    res.json(reactivatedUser);
});

module.exports = router;
