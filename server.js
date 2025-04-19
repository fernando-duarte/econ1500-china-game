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
const cookieParser = require('cookie-parser');
const csrf = require('csurf');
const rateLimit = require('express-rate-limit');
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
app.use(cookieParser());

// CSRF protection for API endpoints
const csrfProtection = csrf({ cookie: { sameSite: 'strict', secure: true } });

// Add CSRF protection to all API routes except GET requests
app.use('/api', (req, res, next) => {
  // Skip CSRF for GET requests
  if (req.method === 'GET') {
    return next();
  }
  csrfProtection(req, res, next);
});

// Provide CSRF token for client
app.get('/api/csrf-token', csrfProtection, (req, res) => {
  res.json({ csrfToken: req.csrfToken() });
});

// Rate limiting middleware
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  headers: true,
  message: { error: 'Too many requests, please try again later.' }
});

// Apply rate limiting to all API routes
app.use('/api/', apiLimiter);

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

// Mutex-like locking mechanism to prevent race conditions
const locks = {
  gameState: false,
  teams: {}
};

// Lock acquisition with timeout
async function acquireLock(lockName, id = null, timeoutMs = 5000) {
  const lockKey = id ? `${lockName}_${id}` : lockName;
  const startTime = Date.now();

  while (locks[lockName] === true || (id && locks[lockName][id] === true)) {
    // Check for timeout
    if (Date.now() - startTime > timeoutMs) {
      throw new Error(`Timeout acquiring lock: ${lockKey}`);
    }
    // Wait a bit before trying again
    await new Promise(resolve => setTimeout(resolve, 50));
  }

  // Acquire the lock
  if (id) {
    if (!locks[lockName]) locks[lockName] = {};
    locks[lockName][id] = true;
  } else {
    locks[lockName] = true;
  }

  return true;
}

// Release a lock
function releaseLock(lockName, id = null) {
  if (id) {
    if (locks[lockName] && locks[lockName][id]) {
      locks[lockName][id] = false;
    }
  } else {
    locks[lockName] = false;
  }
}

// Idempotency helpers
function isTeamDecisionProcessed(teamId, round) {
  return lastProcessed.updateTeam[teamId] === round;
}

function markTeamDecisionProcessed(teamId, round) {
  lastProcessed.updateTeam[teamId] = round;
}

function resetTeamDecisionProcessed(teamId) {
  lastProcessed.updateTeam[teamId] = null;
}

function isGameStartProcessed() {
  return lastProcessed.startGame === true;
}

function markGameStartProcessed() {
  lastProcessed.startGame = true;
}

function resetGameStartProcessed() {
  lastProcessed.startGame = false;
}

function isRoundAdvanceProcessed(round) {
  return lastProcessed.nextRound === round;
}

function markRoundAdvanceProcessed(round) {
  lastProcessed.nextRound = round;
}

function resetRoundAdvanceProcessed() {
  lastProcessed.nextRound = null;
}

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  // Join team room
  socket.on('joinTeam', (teamId) => {
    // Validate teamId
    if (!teamId || typeof teamId !== 'string') {
      return socket.emit('error', { message: 'Invalid team ID' });
    }

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
    // Validate input
    const { teamId, savingsRate, exchangeRate } = data;

    if (!teamId || typeof teamId !== 'string') {
      return socket.emit('error', { message: 'Invalid team ID' });
    }

    if (typeof savingsRate !== 'number') {
      return socket.emit('error', { message: 'Savings rate must be a number' });
    }

    if (savingsRate < 0.01 || savingsRate > 0.99) {
      return socket.emit('error', { message: 'Savings rate must be between 1% and 99%' });
    }

    if (!exchangeRate || typeof exchangeRate !== 'string') {
      return socket.emit('error', { message: 'Invalid exchange rate policy' });
    }

    if (!['fixed', 'market', 'undervalue', 'overvalue'].includes(exchangeRate)) {
      return socket.emit('error', { message: 'Exchange rate policy must be one of: fixed, market, undervalue, overvalue' });
    }

    // Set a timeout for the operation
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Operation timed out')), 5000);
    });

    try {
      // Race the operation against the timeout
      await Promise.race([
        (async () => {
          // Idempotency: Only process if this round is new for this team
          if (gameState.teams[teamId] && !isTeamDecisionProcessed(teamId, gameState.round)) {
            markTeamDecisionProcessed(teamId, gameState.round);

            try {
              // Acquire lock for this team
              await acquireLock('teams', teamId);

              if (gameState.teams[teamId]) {
                // Submit the decision
                const decision = await economicModelService.submitDecision(
                  teamId,
                  savingsRate,
                  exchangeRate
                );

                // Update team data
                gameState.teams[teamId].savingsRate = savingsRate;
                gameState.teams[teamId].exchangeRate = exchangeRate;

                // Broadcast state to team members
                io.to(`team-${teamId}`).emit('teamUpdate', gameState.teams[teamId]);
                io.to(`team-${teamId}`).emit('decisionSubmitted', { success: true });
              }
            } finally {
              // Always release the lock
              releaseLock('teams', teamId);
            }
          }
        })(),
        timeoutPromise
      ]);
    } catch (error) {
      console.error('Error or timeout in updateTeam:', error.message);
      socket.emit('error', {
        message: error.message === 'Operation timed out' ?
          'Request timed out' : 'Failed to submit decision'
      });

      // If it was a timeout, we should reset the idempotency flag
      if (error.message === 'Operation timed out' && isTeamDecisionProcessed(teamId, gameState.round)) {
        resetTeamDecisionProcessed(teamId);
      }
    }
  });

  // Professor control events
  socket.on('startGame', async () => {
    // Idempotency: Only process if not already started
    if (!gameState.isRunning && !isGameStartProcessed()) {
      markGameStartProcessed();

      // Set a timeout for the operation
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Operation timed out')), 5000);
      });

      try {
        // Race the operation against the timeout
        await Promise.race([
          (async () => {
            try {
              // Acquire lock for game state
              await acquireLock('gameState');

              // Start the game
              const result = await economicModelService.startGame();

              // Update our local game state
              gameState.isRunning = true;
              gameState.round = result.current_round;
              gameState.timer = 300;

              // Broadcast updated game state
              io.emit('gameState', gameState);
            } finally {
              // Always release the lock
              releaseLock('gameState');
            }
          })(),
          timeoutPromise
        ]);
      } catch (error) {
        console.error('Error or timeout in startGame:', error.message);
        socket.emit('error', {
          message: error.message === 'Operation timed out' ?
            'Request timed out' : 'Failed to start game'
        });
        // Reset idempotency flag if there was an error
        resetGameStartProcessed();
      }
    }
  });

  socket.on('pauseGame', () => {
    gameState.isRunning = false;
    io.emit('gameState', gameState);
  });

  socket.on('nextRound', async () => {
    // Idempotency: Only process if round is not already advanced
    if (!isRoundAdvanceProcessed(gameState.round) && gameState.round < 10) {
      markRoundAdvanceProcessed(gameState.round);

      // Set a timeout for the operation
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Operation timed out')), 8000); // Longer timeout for round advancement
      });

      try {
        // Race the operation against the timeout
        await Promise.race([
          (async () => {
            try {
              // Acquire lock for game state
              await acquireLock('gameState');

              // Advance the round
              const result = await economicModelService.advanceRound();

              // Get the game state
              const modelGameState = await economicModelService.getGameState();

              // Update our local game state
              gameState.round = modelGameState.current_round;
              gameState.timer = 300;

              // Get all team data in a single pass
              const teamUpdates = {};
              Object.keys(modelGameState.teams).forEach(teamId => {
                if (gameState.teams[teamId]) {
                  const modelTeam = modelGameState.teams[teamId];
                  teamUpdates[teamId] = {
                    output: modelTeam.current_state.GDP,
                    consumption: modelTeam.current_state.Consumption,
                    capital: modelTeam.current_state.Capital,
                    labor: modelTeam.current_state['Labor Force'],
                    netExports: modelTeam.current_state['Net Exports'],
                    productivity: modelTeam.current_state['Productivity (TFP)'],
                    humanCapital: modelTeam.current_state['Human Capital']
                  };
                }
              });

              // Apply updates and save history in a single pass
              for (const teamId of Object.keys(teamUpdates)) {
                try {
                  // Acquire lock for each team
                  await acquireLock('teams', teamId);

                  const team = gameState.teams[teamId];
                  const updates = teamUpdates[teamId];

                  // Save history
                  team.history.push({
                    round: gameState.round - 1,
                    savingsRate: team.savingsRate,
                    exchangeRate: team.exchangeRate,
                    output: team.output,
                    consumption: team.consumption,
                    netExports: team.netExports,
                    capital: team.capital,
                    labor: team.labor
                  });

                  // Apply updates
                  Object.assign(team, updates);
                } finally {
                  // Always release the team lock
                  releaseLock('teams', teamId);
                }
              }

              // Broadcast updated game state
              io.emit('gameState', gameState);
            } finally {
              // Always release the game state lock
              releaseLock('gameState');
            }
          })(),
          timeoutPromise
        ]);
      } catch (error) {
        console.error('Error or timeout in nextRound:', error.message);
        socket.emit('error', {
          message: error.message === 'Operation timed out' ?
            'Request timed out' : 'Failed to advance round'
        });

        // Reset idempotency flag if there was a timeout
        if (error.message === 'Operation timed out') {
          resetRoundAdvanceProcessed();
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

// Helper function for consistent error handling
function handleError(error, res = null, socket = null, errorMessage = 'An error occurred') {
  console.error(`${errorMessage}:`, error.message);

  // For REST API
  if (res) {
    return res.status(500).json({ success: false, message: errorMessage });
  }

  // For Socket.IO
  if (socket) {
    return socket.emit('error', { message: errorMessage });
  }
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
    handleError(error, res, null, 'Failed to check model health');
  }
});

// Game routes
app.get('/api/game', (req, res) => {
  res.json(gameState);
});

app.post('/api/game/start', async (req, res) => {
  try {
    // Use the same logic as the socket event
    if (!gameState.isRunning && !isGameStartProcessed()) {
      markGameStartProcessed();

      try {
        // Acquire lock for game state
        await acquireLock('gameState');

        const result = await economicModelService.startGame();
        gameState.isRunning = true;
        gameState.round = result.current_round;
        gameState.timer = 300;

        // Broadcast to all clients
        io.emit('gameState', gameState);

        res.status(200).json({ success: true, game: gameState });
      } finally {
        // Always release the lock
        releaseLock('gameState');
      }
    } else {
      res.status(400).json({ success: false, message: 'Game already started' });
    }
  } catch (error) {
    resetGameStartProcessed();
    handleError(error, res, null, 'Failed to start game');
  }
});

app.post('/api/game/advance', async (req, res) => {
  try {
    // Use the same logic as the socket event
    if (!isRoundAdvanceProcessed(gameState.round) && gameState.round < 10) {
      markRoundAdvanceProcessed(gameState.round);

      try {
        // Acquire lock for game state
        await acquireLock('gameState');

        const result = await economicModelService.advanceRound();

        // Get game state
        const modelGameState = await economicModelService.getGameState();

        // Update our state
        gameState.round = modelGameState.current_round;
        gameState.timer = 300;

        // Get all team data in a single pass
        const teamUpdates = {};
        Object.keys(modelGameState.teams).forEach(teamId => {
          if (gameState.teams[teamId]) {
            const modelTeam = modelGameState.teams[teamId];
            teamUpdates[teamId] = {
              output: modelTeam.current_state.GDP,
              consumption: modelTeam.current_state.Consumption,
              capital: modelTeam.current_state.Capital,
              labor: modelTeam.current_state['Labor Force'],
              netExports: modelTeam.current_state['Net Exports'],
              productivity: modelTeam.current_state['Productivity (TFP)'],
              humanCapital: modelTeam.current_state['Human Capital']
            };
          }
        });

        // Apply updates and save history in a single pass
        for (const teamId of Object.keys(teamUpdates)) {
          try {
            // Acquire lock for each team
            await acquireLock('teams', teamId);

            const team = gameState.teams[teamId];
            const updates = teamUpdates[teamId];

            // Save history
            team.history.push({
              round: gameState.round - 1,
              savingsRate: team.savingsRate,
              exchangeRate: team.exchangeRate,
              output: team.output,
              consumption: team.consumption,
              netExports: team.netExports,
              capital: team.capital,
              labor: team.labor
            });

            // Apply updates
            Object.assign(team, updates);
          } finally {
            // Always release the team lock
            releaseLock('teams', teamId);
          }
        }

        // Broadcast to all clients
        io.emit('gameState', gameState);

        res.status(200).json({ success: true, game: gameState });
      } finally {
        // Always release the game state lock
        releaseLock('gameState');
      }
    } else if (gameState.round >= 10) {
      res.status(400).json({ success: false, message: 'Game already ended' });
    } else {
      res.status(400).json({ success: false, message: 'Round already processed' });
    }
  } catch (error) {
    handleError(error, res, null, 'Failed to advance round');
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
    handleError(error, res, null, 'Failed to create team');
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
    if (!isTeamDecisionProcessed(teamId, gameState.round)) {
      markTeamDecisionProcessed(teamId, gameState.round);

      try {
        // Acquire lock for this team
        await acquireLock('teams', teamId);

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
      } finally {
        // Always release the lock
        releaseLock('teams', teamId);
      }
    } else {
      res.status(400).json({ success: false, message: 'Decision already submitted for this round' });
    }
  } catch (error) {
    handleError(error, res, null, 'Failed to submit decision');
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
    res.send('China Growth Game API Server - Access the UI through the frontend');
  });
}

// Start server
server.listen(port, () => {
  console.log(`Unified server listening on port ${port}`);
});