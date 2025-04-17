const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const EconomicModelService = require('./services/economic-model-service');

// Import routes
const gameRoutes = require('./routes/game-routes');
const teamRoutes = require('./routes/team-routes');
const resultsRoutes = require('./routes/results-routes');

// Initialize services
const economicModelService = new EconomicModelService();

// Initialize Express app
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: ['http://localhost:3001'], // Allow React development server
    methods: ['GET', 'POST'],
    credentials: true
  }
});

// Middleware
app.use(cors({
  origin: ['http://localhost:3001'], // Allow React development server
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  credentials: true
}));
app.use(express.json());

// API routes
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'ok', message: 'Server is running' });
});

app.get('/api/economic-model/health', async (req, res) => {
  try {
    const result = await economicModelService.healthCheck();
    res.status(200).json({ status: 'ok', message: result.message });
  } catch (error) {
    res.status(500).json({ status: 'error', message: 'Could not connect to economic model' });
  }
});

// API routes
app.use('/api/game', gameRoutes);
app.use('/api/teams', teamRoutes);
app.use('/api/results', resultsRoutes);

// Serve static files from the React app in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../build')));
  
  // Handle React routing, return all requests to React app
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../build', 'index.html'));
  });
} else {
  // In development, serve the public directory
  app.use(express.static(path.join(__dirname, 'public')));
}

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('New client connected:', socket.id);
  
  // Send initial game state to new clients
  economicModelService.getGameState()
    .then(gameState => {
      socket.emit('gameState', gameState);
    })
    .catch(error => {
      console.error('Failed to get initial game state:', error.message);
    });
  
  // Handle team creation
  socket.on('createTeam', async (teamName) => {
    try {
      const team = await economicModelService.createTeam(teamName);
      io.emit('teamCreated', team);
      
      // Update all clients with new game state
      const gameState = await economicModelService.getGameState();
      io.emit('gameState', gameState);
    } catch (error) {
      socket.emit('error', { message: 'Failed to create team', error: error.message });
    }
  });
  
  // Handle team decision submission
  socket.on('submitDecision', async ({ teamId, savingsRate, exchangeRatePolicy }) => {
    try {
      const decision = await economicModelService.submitDecision(
        teamId,
        savingsRate,
        exchangeRatePolicy
      );
      socket.emit('decisionSubmitted', decision);
    } catch (error) {
      socket.emit('error', { message: 'Failed to submit decision', error: error.message });
    }
  });
  
  // Handle game state changes (for professor)
  socket.on('startGame', async () => {
    try {
      const gameState = await economicModelService.startGame();
      io.emit('gameStarted', gameState);
      io.emit('gameState', gameState);
    } catch (error) {
      socket.emit('error', { message: 'Failed to start game', error: error.message });
    }
  });
  
  socket.on('advanceRound', async () => {
    try {
      const result = await economicModelService.advanceRound();
      io.emit('roundAdvanced', result);
      
      // Update all clients with new game state
      const gameState = await economicModelService.getGameState();
      io.emit('gameState', gameState);
    } catch (error) {
      socket.emit('error', { message: 'Failed to advance round', error: error.message });
    }
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 