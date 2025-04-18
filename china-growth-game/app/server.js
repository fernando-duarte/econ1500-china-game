const express = require('express');
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

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 