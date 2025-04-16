const express = require('express');
const router = express.Router();
const EconomicModelService = require('../services/economic-model-service');

// Initialize the economic model service
const economicModelService = new EconomicModelService();

/**
 * @route   POST /api/game/init
 * @desc    Initialize a new game
 * @access  Public
 */
router.post('/init', async (req, res) => {
  try {
    const gameState = await economicModelService.initializeGame();
    res.status(200).json(gameState);
  } catch (error) {
    res.status(500).json({ 
      message: 'Failed to initialize game',
      error: error.message 
    });
  }
});

/**
 * @route   POST /api/game/start
 * @desc    Start the game with registered teams
 * @access  Public
 */
router.post('/start', async (req, res) => {
  try {
    const gameState = await economicModelService.startGame();
    res.status(200).json(gameState);
  } catch (error) {
    res.status(500).json({ 
      message: 'Failed to start game',
      error: error.message 
    });
  }
});

/**
 * @route   POST /api/game/next-round
 * @desc    Advance to the next round
 * @access  Public
 */
router.post('/next-round', async (req, res) => {
  try {
    const result = await economicModelService.advanceRound();
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ 
      message: 'Failed to advance to next round',
      error: error.message 
    });
  }
});

/**
 * @route   GET /api/game/state
 * @desc    Get the current game state
 * @access  Public
 */
router.get('/state', async (req, res) => {
  try {
    const gameState = await economicModelService.getGameState();
    res.status(200).json(gameState);
  } catch (error) {
    res.status(500).json({ 
      message: 'Failed to get game state',
      error: error.message 
    });
  }
});

module.exports = router; 