const express = require('express');
const router = express.Router();
const EconomicModelService = require('../services/economic-model-service');

// Initialize the economic model service
const economicModelService = new EconomicModelService();

/**
 * @route   POST /api/teams/create
 * @desc    Create a new team
 * @access  Public
 */
router.post('/create', async (req, res) => {
  try {
    const { team_name } = req.body;
    const team = await economicModelService.createTeam(team_name);
    res.status(201).json(team);
  } catch (error) {
    res.status(500).json({ 
      message: 'Failed to create team',
      error: error.message 
    });
  }
});

/**
 * @route   POST /api/teams/decisions
 * @desc    Submit a team's decision for the current round
 * @access  Public
 */
router.post('/decisions', async (req, res) => {
  try {
    const { team_id, savings_rate, exchange_rate_policy } = req.body;
    
    // Validate inputs
    if (!team_id) {
      return res.status(400).json({ message: 'Team ID is required' });
    }
    
    if (typeof savings_rate !== 'number' || savings_rate < 0.01 || savings_rate > 0.99) {
      return res.status(400).json({ message: 'Savings rate must be between 1% and 99%' });
    }
    
    if (!['undervalue', 'market', 'overvalue'].includes(exchange_rate_policy)) {
      return res.status(400).json({ 
        message: "Exchange rate policy must be 'undervalue', 'market', or 'overvalue'" 
      });
    }
    
    const decision = await economicModelService.submitDecision(
      team_id,
      savings_rate,
      exchange_rate_policy
    );
    
    res.status(200).json(decision);
  } catch (error) {
    res.status(500).json({ 
      message: 'Failed to submit decision',
      error: error.message 
    });
  }
});

/**
 * @route   GET /api/teams/:teamId
 * @desc    Get a team's state
 * @access  Public
 */
router.get('/:teamId', async (req, res) => {
  try {
    const { teamId } = req.params;
    const teamState = await economicModelService.getTeamState(teamId);
    res.status(200).json(teamState);
  } catch (error) {
    res.status(500).json({ 
      message: `Failed to get team state for ${req.params.teamId}`,
      error: error.message 
    });
  }
});

/**
 * @route   GET /api/teams/:teamId/visualizations
 * @desc    Get visualization data for a team
 * @access  Public
 */
router.get('/:teamId/visualizations', async (req, res) => {
  try {
    const { teamId } = req.params;
    const visualizations = await economicModelService.getTeamVisualizations(teamId);
    res.status(200).json(visualizations);
  } catch (error) {
    res.status(500).json({ 
      message: `Failed to get visualizations for team ${req.params.teamId}`,
      error: error.message 
    });
  }
});

module.exports = router; 