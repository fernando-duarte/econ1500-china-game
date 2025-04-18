const express = require('express');
const router = express.Router();

// Get game state
router.get('/', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'Game state retrieved'
  });
});

// Start game
router.post('/start', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'Game started'
  });
});

// Advance round
router.post('/advance', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'Round advanced'
  });
});

module.exports = router; 