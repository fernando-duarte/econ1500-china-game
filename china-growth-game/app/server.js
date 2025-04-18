/**
 * Legacy Server Wrapper
 *
 * This file is a wrapper around the unified server implementation.
 * It redirects to the unified server to maintain backward compatibility.
 *
 * For new development, use the unified-server.js directly.
 */

const express = require('express');
const path = require('path');

// Determine if we should run in legacy mode or redirect to unified server
const LEGACY_MODE = process.env.LEGACY_MODE === 'true';

if (!LEGACY_MODE) {
  console.log('Running in redirect mode - forwarding to unified server');
  // Load the unified server directly
  require('../../../unified-server');
  // This process will exit as the unified server takes over
  process.exit(0);
}

// If we're here, we're running in legacy mode for backward compatibility
console.log('Running in legacy mode - this is deprecated and will be removed in a future version');

const EconomicModelService = require('./services/economic-model-service');

// Initialize services
const economicModelService = new EconomicModelService();

// Create a minimal Express app
const app = express();

// Body parser middleware
app.use(express.json());

// Simple health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', message: 'Server is running' });
});

// Simple API endpoint
app.get('/api/hello', (req, res) => {
  res.status(200).json({ message: 'Hello, world!' });
});

// Model health check
app.get('/api/model/health', async (req, res) => {
  try {
    const health = await economicModelService.healthCheck();
    res.status(200).json(health);
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// Game routes
app.get('/api/game', async (req, res) => {
  try {
    const gameState = await economicModelService.getGameState();
    res.status(200).json({ success: true, game: gameState });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

app.post('/api/game/start', async (req, res) => {
  try {
    const result = await economicModelService.startGame();
    res.status(200).json({ success: true, game: result });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

app.post('/api/game/advance', async (req, res) => {
  try {
    const result = await economicModelService.advanceRound();
    res.status(200).json({ success: true, game: result });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Team routes
app.get('/api/teams', async (req, res) => {
  try {
    const gameState = await economicModelService.getGameState();
    res.status(200).json({ success: true, teams: gameState.teams });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

app.post('/api/teams', async (req, res) => {
  try {
    const { name } = req.body;
    const team = await economicModelService.createTeam(name);
    res.status(201).json({ success: true, team });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

app.get('/api/teams/:teamId', async (req, res) => {
  try {
    const { teamId } = req.params;
    const gameState = await economicModelService.getGameState();
    const team = gameState.teams.find(t => t.id === teamId);

    if (!team) {
      return res.status(404).json({ success: false, message: 'Team not found' });
    }

    res.status(200).json({ success: true, team });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

app.post('/api/teams/:teamId/decisions', async (req, res) => {
  try {
    const { teamId } = req.params;
    const { savingsRate, exchangeRatePolicy } = req.body;

    const decision = await economicModelService.submitDecision(
      teamId,
      savingsRate,
      exchangeRatePolicy
    );

    res.status(201).json({ success: true, decision });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Serve static files from the React build directory if available
const buildPath = path.join(__dirname, '..', 'build');
if (require('fs').existsSync(buildPath)) {
  console.log('Serving static files from', buildPath);
  app.use(express.static(buildPath));

  // Handle React routing, return all requests to React app
  app.get('*', (req, res) => {
    res.sendFile(path.join(buildPath, 'index.html'));
  });
} else {
  console.log('No build directory found, only API endpoints will be available');
  // If no build directory, at least provide some response at the root
  app.get('/', (req, res) => {
    res.send('China Growth Game API Server - Build the frontend or use the dev server to access the UI');
  });
}

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});