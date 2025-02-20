const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const userRoutes = require('./routes/userRoutes');

// Initialize app
const app = express();

// Middleware
app.use(express.json());
app.use(cors());

// Connect to MongoDB (adjust your MongoDB URI)
mongoose.connect('mongodb://localhost:27017/user-management', { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log("Connected to MongoDB"))
    .catch(err => console.log(err));

// Routes
app.use('/api/users', userRoutes);

// Start server
const port = 5000;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
