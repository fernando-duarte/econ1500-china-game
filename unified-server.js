/**
 * Unified Server for China's Growth Game
 * 
 * This server combines the functionality of both existing server implementations:
 * - Socket.IO real-time communication from backend/server.js
 * - RESTful API structure from china-growth-game/app/server.js
 * - Consolidated economic model integration
 */

const express = require('express');
const http = require('http');
const path = require('path');
const cors = require('cors');
const { Server } = require('socket.io');
const axios = require('axios');
require('dotenv').config();

// Load economic model service
const EconomicModelService = require('./services/economic-model-service');
const economicModelService = new EconomicModelService();

// Express and HTTP server setup
const app = express();
const server = http.createServer(app);

// Environment variables
const port = process.env.PORT || 4000;
const modelApiUrl = process.env.MODEL_API_URL || 'http://model:8000';
const allowedOrigins = process.env.ALLOWED_ORIGINS || 'http://localhost:3000';
const originsArray = allowedOrigins.split(',');

// Middleware
app.use(cors({
  origin: originsArray,
  credentials: true
}));
app.use(express.json());

// Socket.IO setup
const io = new Server(server, {
  cors: {
    origin: originsArray,
    methods: ['GET', 'POST'],
    credentials: true
  }
});

// Game state
let gameState = {
  round: 0,
  timer: 300, // 5 minutes per round
  isRunning: false,
  teams: {}
};

// Idempotency state
const lastProcessed = {
  updateTeam: {}, // teamId: round
  startGame: null,
  nextRound: null
};

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  // Join team room
  socket.on('joinTeam', (teamId) => {
    socket.join(`team-${teamId}`);

    // Initialize team if not exists
    if (!gameState.teams[teamId]) {
      gameState.teams[teamId] = {
        id: teamId,
        name: `Team ${teamId}`,
        savingsRate: 0.3,
        exchangeRate: 'fixed',
        capital: 100,
        labor: 100,
        score: 0,
        history: []
      };
    }

    // Send current game state to new user
    socket.emit('gameState', gameState);
  });

  // Handle team decisions
  socket.on('updateTeam', async (data) => {
    const { teamId, savingsRate, exchangeRate } = data;
    // Idempotency: Only process if this round is new for this team
    if (gameState.teams[teamId] && lastProcessed.updateTeam[teamId] !== gameState.round) {
      lastProcessed.updateTeam[teamId] = gameState.round;
      if (gameState.teams[teamId]) {
        try {
          // Submit the decision
          const decision = await economicModelService.submitDecision(
            teamId, 
            savingsRate, 
            exchangeRate === 'fixed' ? 'market' : exchangeRate
          );

          // Update team data
          gameState.teams[teamId].savingsRate = savingsRate;
          gameState.teams[teamId].exchangeRate = exchangeRate;

          // Broadcast updated state to team members
          io.to(`team-${teamId}`).emit('teamUpdate', gameState.teams[teamId]);
          io.to(`team-${teamId}`).emit('decisionSubmitted', { success: true });
        } catch (error) {
          console.error('Error submitting decision:', error.message);
          socket.emit('error', { message: 'Failed to submit decision' });
        }
      }
    }
  });

  // Professor control events
  socket.on('startGame', async () => {
    // Idempotency: Only process if not already started
    if (!gameState.isRunning && lastProcessed.startGame !== true) {
      lastProcessed.startGame = true;

      try {
        // Start the game
        const result = await economicModelService.startGame();

        // Update our local game state
        gameState.isRunning = true;
        gameState.round = result.current_round;
        gameState.timer = 300;

        // Broadcast updated game state
        io.emit('gameState', gameState);
      } catch (error) {
        console.error('Error starting game:', error.message);
        socket.emit('error', { message: 'Failed to start game' });
        // Reset idempotency flag if there was an error
        lastProcessed.startGame = false;
      }
    }
  });

  socket.on('pauseGame', () => {
    gameState.isRunning = false;
    io.emit('gameState', gameState);
  });

  socket.on('nextRound', async () => {
    // Idempotency: Only process if round is not already advanced
    if (lastProcessed.nextRound !== gameState.round && gameState.round < 10) {
      lastProcessed.nextRound = gameState.round;

      try {
        // Advance the round
        const result = await economicModelService.advanceRound();
        
        // Get the updated game state
        const modelGameState = await economicModelService.getGameState();

        // Update our local game state
        gameState.round = modelGameState.current_round;
        gameState.timer = 300;

        // Update all teams with data from the model
        Object.keys(modelGameState.teams).forEach(teamId => {
          if (gameState.teams[teamId]) {
            const modelTeam = modelGameState.teams[teamId];
            const team = gameState.teams[teamId];

            // Save history
            team.history.push({
              round: gameState.round - 1,
              savingsRate: team.savingsRate,
              exchangeRate: team.exchangeRate,
              output: team.output,
              consumption: team.consumption
            });

            // Update team data from model
            team.output = modelTeam.current_state.GDP;
            team.consumption = modelTeam.current_state.Consumption;
            team.capital = modelTeam.current_state.Capital;
            team.labor = modelTeam.current_state['Labor Force'];
          }
        });

        // Broadcast updated game state
        io.emit('gameState', gameState);
      } catch (error) {
        console.error('Error advancing round:', error.message);
        socket.emit('error', { message: 'Failed to advance round' });
      }
    } else if (gameState.round >= 10 && !gameState.isRunning) {
      // End of game
      io.emit('gameEnd', calculateFinalScores());
    }
  });

  // Disconnect handling
  socket.on('disconnect', () => {
    console.log(`User disconnected: ${socket.id}`);
  });
});

// Helper function to calculate final scores
function calculateFinalScores() {
  const scores = {};

  Object.keys(gameState.teams).forEach(teamId => {
    const team = gameState.teams[teamId];
    // Simple scoring: sum of consumption across all rounds
    const totalConsumption = team.history.reduce((sum, round) => sum + (round.consumption || 0), 0);
    scores[teamId] = totalConsumption;
    team.score = totalConsumption;
  });

  return scores;
}

// ==========================
// REST API Endpoints
// ==========================

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', message: 'Unified server is running' });
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
app.get('/api/game', (req, res) => {
  res.json(gameState);
});

app.post('/api/game/start', async (req, res) => {
  try {
    // Use the same logic as the socket event
    if (!gameState.isRunning && lastProcessed.startGame !== true) {
      lastProcessed.startGame = true;
      const result = await economicModelService.startGame();
      gameState.isRunning = true;
      gameState.round = result.current_round;
      gameState.timer = 300;
      
      // Broadcast to all clients
      io.emit('gameState', gameState);
      
      res.status(200).json({ success: true, game: gameState });
    } else {
      res.status(400).json({ success: false, message: 'Game already started' });
    }
  } catch (error) {
    lastProcessed.startGame = false;
    res.status(500).json({ success: false, message: error.message });
  }
});

app.post('/api/game/advance', async (req, res) => {
  try {
    // Use the same logic as the socket event
    if (lastProcessed.nextRound !== gameState.round && gameState.round < 10) {
      lastProcessed.nextRound = gameState.round;
      const result = await economicModelService.advanceRound();
      
      // Get updated game state
      const modelGameState = await economicModelService.getGameState();
      
      // Update our state
      gameState.round = modelGameState.current_round;
      gameState.timer = 300;
      
      // Process team updates
      // ...
      
      // Broadcast to all clients
      io.emit('gameState', gameState);
      
      res.status(200).json({ success: true, game: gameState });
    } else if (gameState.round >= 10) {
      res.status(400).json({ success: false, message: 'Game already ended' });
    } else {
      res.status(400).json({ success: false, message: 'Round already processed' });
    }
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Team routes
app.get('/api/teams', (req, res) => {
  res.json(gameState.teams);
});

app.get('/api/teams/:id', (req, res) => {
  const teamId = req.params.id;
  if (gameState.teams[teamId]) {
    res.json(gameState.teams[teamId]);
  } else {
    res.status(404).json({ error: 'Team not found' });
  }
});

app.post('/api/teams', async (req, res) => {
  try {
    const { name } = req.body;
    const team = await economicModelService.createTeam(name);
    
    // Add to local state
    const teamId = team.id;
    gameState.teams[teamId] = {
      id: teamId,
      name: team.name,
      savingsRate: 0.3,
      exchangeRate: 'market',
      score: 0,
      history: []
    };
    
    res.status(201).json({ success: true, team: gameState.teams[teamId] });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

app.post('/api/teams/:teamId/decisions', async (req, res) => {
  try {
    const { teamId } = req.params;
    const { savingsRate, exchangeRatePolicy } = req.body;
    
    if (!gameState.teams[teamId]) {
      return res.status(404).json({ success: false, message: 'Team not found' });
    }
    
    // Process the same way as socket
    if (lastProcessed.updateTeam[teamId] !== gameState.round) {
      lastProcessed.updateTeam[teamId] = gameState.round;
      
      const decision = await economicModelService.submitDecision(
        teamId,
        savingsRate,
        exchangeRatePolicy
      );
      
      // Update local state
      gameState.teams[teamId].savingsRate = savingsRate;
      gameState.teams[teamId].exchangeRate = exchangeRatePolicy;
      
      // Emit to team channel
      io.to(`team-${teamId}`).emit('teamUpdate', gameState.teams[teamId]);
      
      res.status(201).json({ success: true, decision });
    } else {
      res.status(400).json({ success: false, message: 'Decision already submitted for this round' });
    }
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Serve static files from the React build directory if available
const buildPath = path.join(__dirname, 'build');
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
server.listen(port, () => {
  console.log(`Unified server listening on port ${port}`);
}); 