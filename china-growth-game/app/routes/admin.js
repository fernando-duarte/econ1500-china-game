const express = require('express');
const router = express.Router();
const { isAuthenticated, isAdmin } = require('../middleware/auth');
const featureFlags = require('../config/featureFlags');

// Get all feature flags
router.get('/feature-flags', isAuthenticated, isAdmin, async (req, res) => {
  try {
    const flags = await featureFlags.getAllFeatures();
    res.status(200).json({ success: true, flags });
  } catch (error) {
    console.error('Error fetching feature flags:', error);
    res.status(500).json({ success: false, message: 'Failed to fetch feature flags' });
  }
});

// Update a feature flag
router.post('/feature-flags', isAuthenticated, isAdmin, async (req, res) => {
  try {
    const { key, enabled, scope, id } = req.body;
    
    if (!key || enabled === undefined) {
      return res.status(400).json({ 
        success: false, 
        message: 'Feature key and enabled status are required' 
      });
    }
    
    const flags = await featureFlags.overrideFeature(key, enabled, { scope, id });
    res.status(200).json({ success: true, flags });
  } catch (error) {
    console.error('Error updating feature flag:', error);
    res.status(500).json({ success: false, message: 'Failed to update feature flag' });
  }
});

// Check if a feature is enabled for a class
router.get('/feature-flags/:key/class/:classId', isAuthenticated, async (req, res) => {
  try {
    const { key, classId } = req.params;
    const isEnabled = await featureFlags.isFeatureEnabledForClass(key, classId);
    res.status(200).json({ success: true, isEnabled });
  } catch (error) {
    console.error('Error checking feature flag:', error);
    res.status(500).json({ success: false, message: 'Failed to check feature flag' });
  }
});

// Check if a feature is enabled for a team
router.get('/feature-flags/:key/team/:teamId', isAuthenticated, async (req, res) => {
  try {
    const { key, teamId } = req.params;
    const isEnabled = await featureFlags.isFeatureEnabledForTeam(key, teamId);
    res.status(200).json({ success: true, isEnabled });
  } catch (error) {
    console.error('Error checking feature flag:', error);
    res.status(500).json({ success: false, message: 'Failed to check feature flag' });
  }
});

// Reset feature flag cache
router.post('/feature-flags/reset-cache', isAuthenticated, isAdmin, (req, res) => {
  try {
    featureFlags.clearCache();
    res.status(200).json({ success: true, message: 'Feature flag cache cleared' });
  } catch (error) {
    console.error('Error clearing feature flag cache:', error);
    res.status(500).json({ success: false, message: 'Failed to clear feature flag cache' });
  }
});

// Add admin endpoints for game management
router.get('/games', isAuthenticated, isAdmin, (req, res) => {
  // Implementation for fetching all active games
  res.status(200).json({ success: true, games: [] });
});

router.post('/games/:gameId/reset', isAuthenticated, isAdmin, (req, res) => {
  // Implementation for resetting a game
  const { gameId } = req.params;
  res.status(200).json({ success: true, message: `Game ${gameId} reset` });
});

router.post('/games/:gameId/advance-round', isAuthenticated, isAdmin, (req, res) => {
  // Implementation for advancing a round
  const { gameId } = req.params;
  res.status(200).json({ success: true, message: `Game ${gameId} advanced to next round` });
});

router.post('/games/:gameId/events', isAuthenticated, isAdmin, (req, res) => {
  // Implementation for triggering an event
  const { gameId } = req.params;
  const { eventType } = req.body;
  res.status(200).json({ 
    success: true, 
    message: `Event ${eventType} triggered for game ${gameId}` 
  });
});

router.get('/games/:gameId/export', isAuthenticated, isAdmin, (req, res) => {
  // Implementation for exporting game data
  const { gameId } = req.params;
  res.status(200).json({ 
    success: true, 
    message: `Game data for ${gameId} exported` 
  });
});

module.exports = router; 