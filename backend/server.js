/**
 * Legacy Server Wrapper
 *
 * This file is a wrapper around the unified server implementation.
 * It redirects to the unified server to maintain backward compatibility.
 *
 * For new development, use the unified-server.js directly.
 */

const express = require('express');
const http = require('http');
const path = require('path');
const cors = require('cors');
const { Server } = require('socket.io');
const axios = require('axios');
require('dotenv').config();

// Determine if we should run in legacy mode or redirect to unified server
const LEGACY_MODE = process.env.LEGACY_MODE === 'true';

if (!LEGACY_MODE) {
  console.log('Running in redirect mode - forwarding to unified server');
  // Load the unified server directly
  require('../unified-server');
  // This process will exit as the unified server takes over
  process.exit(0);
}

// If we're here, we're running in legacy mode for backward compatibility
console.log('Running in legacy mode - this is deprecated and will be removed in a future version');

const app = express();
const server = http.createServer(app);

const port = process.env.PORT || 4000;
const modelApiUrl = process.env.MODEL_API_URL || 'http://model:8000';

// Middleware
const allowedOrigins = process.env.ALLOWED_ORIGINS || 'http://localhost:3000';
const originsArray = allowedOrigins.split(',');

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
        // Update team decisions
        gameState.teams[teamId].savingsRate = savingsRate;
        gameState.teams[teamId].exchangeRate = exchangeRate;

        // Broadcast updated state to team members
        io.to(`team-${teamId}`).emit('teamUpdate', gameState.teams[teamId]);

        // Submit decision to the model API
        try {
          // First, check if the team exists in the model
          let teamExists = false;
          try {
            await axios.get(`${modelApiUrl}/teams/${teamId}`);
            teamExists = true;
          } catch (error) {
            if (error.response && error.response.status === 404) {
              // Team doesn't exist, create it
              await axios.post(`${modelApiUrl}/teams/create`, {
                team_name: gameState.teams[teamId].name
              });
            } else {
              throw error;
            }
          }

          // Submit the decision
          const response = await axios.post(`${modelApiUrl}/teams/decisions`, {
            team_id: teamId,
            savings_rate: savingsRate,
            exchange_rate_policy: exchangeRate // Conversion handled in the service layer
          });

          // Get the updated team state
          const teamState = await axios.get(`${modelApiUrl}/teams/${teamId}`);

          // Update team data with model results
          const currentState = teamState.data.current_state;
          gameState.teams[teamId].output = currentState.GDP;
          gameState.teams[teamId].consumption = currentState.Consumption;
          gameState.teams[teamId].nextCapital = currentState.Capital;

          // Broadcast results to team
          io.to(`team-${teamId}`).emit('calculationResults', {
            output: currentState.GDP,
            consumption: currentState.Consumption,
            investment: currentState.Investment,
            next_capital: currentState.Capital
          });
        } catch (error) {
          console.error('Error calculating economic outcomes:', error.message);
          if (error.response) {
            console.error('Response data:', error.response.data);
          }
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
        // Initialize the game in the model API
        await axios.post(`${modelApiUrl}/game/init`);

        // Start the game in the model API
        const response = await axios.post(`${modelApiUrl}/game/start`);

        // Update our local game state
        gameState.isRunning = true;
        gameState.round = response.data.current_round;
        gameState.timer = 300;

        // Broadcast updated game state
        io.emit('gameState', gameState);
      } catch (error) {
        console.error('Error starting game:', error.message);
        if (error.response) {
          console.error('Response data:', error.response.data);
        }
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
        // Call the model API to advance the round
        const response = await axios.post(`${modelApiUrl}/game/next-round`);

        // Get the updated game state
        const modelGameState = await axios.get(`${modelApiUrl}/game/state`);

        // Update our local game state
        gameState.round = modelGameState.data.current_round;
        gameState.timer = 300;

        // Update all teams with data from the model
        const modelTeams = modelGameState.data.teams;
        Object.keys(modelTeams).forEach(teamId => {
          if (gameState.teams[teamId]) {
            const modelTeam = modelTeams[teamId];
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
        if (error.response) {
          console.error('Response data:', error.response.data);
        }
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

// API endpoints
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

app.get('/api/game', (req, res) => {
  res.json(gameState);
});

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

// Start server
server.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});