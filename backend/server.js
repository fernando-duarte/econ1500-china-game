const express = require('express');
const http = require('http');
const cors = require('cors');
const { Server } = require('socket.io');
const axios = require('axios');
require('dotenv').config();

const app = express();
const server = http.createServer(app);

const port = process.env.PORT || 4000;
const modelApiUrl = process.env.MODEL_API_URL || 'http://model:8000';

// Middleware
app.use(cors());
app.use(express.json());

// Socket.IO setup
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// Game state
let gameState = {
  round: 0,
  timer: 300, // 5 minutes per round
  isRunning: false,
  teams: {}
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
    
    if (gameState.teams[teamId]) {
      // Update team decisions
      gameState.teams[teamId].savingsRate = savingsRate;
      gameState.teams[teamId].exchangeRate = exchangeRate;
      
      // Broadcast updated state to team members
      io.to(`team-${teamId}`).emit('teamUpdate', gameState.teams[teamId]);
      
      // Calculate economic outcomes
      try {
        const response = await axios.post(`${modelApiUrl}/calculate`, {
          savings_rate: savingsRate,
          capital: gameState.teams[teamId].capital,
          labor: gameState.teams[teamId].labor,
          exchange_rate: exchangeRate
        });
        
        // Update team data with model results
        const results = response.data;
        gameState.teams[teamId].output = results.output;
        gameState.teams[teamId].consumption = results.consumption;
        gameState.teams[teamId].nextCapital = results.next_capital;
        
        // Broadcast results to team
        io.to(`team-${teamId}`).emit('calculationResults', results);
      } catch (error) {
        console.error('Error calculating economic outcomes:', error.message);
      }
    }
  });
  
  // Professor control events
  socket.on('startGame', () => {
    gameState.isRunning = true;
    gameState.round = 1;
    gameState.timer = 300;
    io.emit('gameState', gameState);
  });
  
  socket.on('pauseGame', () => {
    gameState.isRunning = false;
    io.emit('gameState', gameState);
  });
  
  socket.on('nextRound', () => {
    if (gameState.round < 10) {
      gameState.round++;
      gameState.timer = 300;
      
      // Update all teams for the new round
      Object.keys(gameState.teams).forEach(teamId => {
        const team = gameState.teams[teamId];
        
        // Save history
        team.history.push({
          round: gameState.round - 1,
          savingsRate: team.savingsRate,
          exchangeRate: team.exchangeRate,
          output: team.output,
          consumption: team.consumption
        });
        
        // Update capital for next round
        if (team.nextCapital) {
          team.capital = team.nextCapital;
        }
      });
      
      io.emit('gameState', gameState);
    } else {
      // End of game
      gameState.isRunning = false;
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