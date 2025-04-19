const express = require('express');
const router = express.Router();
const EconomicModelService = require('../../../services/economic-model-service');

// Initialize the economic model service
const economicModelService = new EconomicModelService();

/**
 * @route   GET /api/results/rankings
 * @desc    Get current rankings
 * @access  Public
 */
router.get('/rankings', async (req, res) => {
  try {
    const rankings = await economicModelService.getRankings();
    res.status(200).json(rankings);
  } catch (error) {
    res.status(500).json({
      message: 'Failed to get rankings',
      error: error.message
    });
  }
});

/**
 * @route   GET /api/results/leaderboard
 * @desc    Get formatted leaderboard with team names
 * @access  Public
 */
router.get('/leaderboard', async (req, res) => {
  try {
    // Get the game state to access team information
    const gameState = await economicModelService.getGameState();
    const rankings = await economicModelService.getRankings();

    // Format the leaderboard with team names
    const formatLeaderboard = (rankingIds, metric) => {
      return rankingIds.map((teamId, index) => {
        const team = gameState.teams[teamId];
        return {
          rank: index + 1,
          team_id: teamId,
          team_name: team.team_name,
          value: team.current_state[metric],
          metric
        };
      });
    };

    const leaderboard = {
      gdp: formatLeaderboard(rankings.gdp || [], 'Y'),
      net_exports: formatLeaderboard(rankings.net_exports || [], 'NX'),
      balanced_economy: rankings.balanced_economy ? rankings.balanced_economy.map((teamId, index) => {
        const team = gameState.teams[teamId];
        const balancedScore = team.current_state.Y + team.current_state.C;
        return {
          rank: index + 1,
          team_id: teamId,
          team_name: team.team_name,
          value: balancedScore,
          metric: 'balanced_economy'
        };
      }) : []
    };

    res.status(200).json(leaderboard);
  } catch (error) {
    res.status(500).json({
      message: 'Failed to get leaderboard',
      error: error.message
    });
  }
});

module.exports = router;