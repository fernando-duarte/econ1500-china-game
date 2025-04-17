const axios = require('axios');

class EconomicModelService {
  constructor(baseUrl) {
    this.baseUrl = baseUrl || process.env.ECONOMIC_MODEL_URL || 'http://localhost:8000';
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async healthCheck() {
    try {
      const response = await this.client.get('/');
      return response.data;
    } catch (error) {
      console.error('Economic model health check failed:', error.message);
      throw error;
    }
  }

  // Legacy method for backward compatibility
  async runSimulation(simulationData) {
    try {
      const response = await this.client.post('/simulate', simulationData);
      return response.data;
    } catch (error) {
      console.error('Economic model simulation failed:', error.message);
      throw error;
    }
  }

  // Game flow methods
  async initializeGame() {
    try {
      const response = await this.client.post('/game/init');
      return response.data;
    } catch (error) {
      console.error('Failed to initialize game:', error.message);
      throw error;
    }
  }

  async startGame() {
    try {
      const response = await this.client.post('/game/start');
      return response.data;
    } catch (error) {
      console.error('Failed to start game:', error.message);
      throw error;
    }
  }

  async advanceRound() {
    try {
      const response = await this.client.post('/game/next-round');
      return response.data;
    } catch (error) {
      console.error('Failed to advance round:', error.message);
      throw error;
    }
  }

  async getGameState() {
    try {
      const response = await this.client.get('/game/state');
      return response.data;
    } catch (error) {
      console.error('Failed to get game state:', error.message);
      throw error;
    }
  }

  // Team management methods
  async createTeam(teamName = null) {
    try {
      const response = await this.client.post('/teams/create', { team_name: teamName });
      return response.data;
    } catch (error) {
      console.error('Failed to create team:', error.message);
      throw error;
    }
  }

  async submitDecision(teamId, savingsRate, exchangeRatePolicy) {
    try {
      const response = await this.client.post('/teams/decisions', {
        team_id: teamId,
        savings_rate: savingsRate,
        exchange_rate_policy: exchangeRatePolicy
      });
      return response.data;
    } catch (error) {
      console.error('Failed to submit decision:', error.message);
      throw error;
    }
  }

  async getTeamState(teamId) {
    try {
      const response = await this.client.get(`/teams/${teamId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get team state for ${teamId}:`, error.message);
      throw error;
    }
  }

  // Results and visualization methods
  async getRankings() {
    try {
      const response = await this.client.get('/results/rankings');
      return response.data;
    } catch (error) {
      console.error('Failed to get rankings:', error.message);
      throw error;
    }
  }

  async getTeamVisualizations(teamId) {
    try {
      const response = await this.client.get(`/results/visualizations/${teamId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get visualizations for team ${teamId}:`, error.message);
      throw error;
    }
  }

  // Default parameters and initial conditions as specified in specs
  getDefaultParameters() {
    return {
      alpha: 0.3,
      delta: 0.1,
      g: 0.005,
      theta: 0.1453,
      phi: 0.1,
      s: 0.2, // Default savings rate, will be changed by students
      beta: -90,
      n: 0.00717,
      eta: 0.02
    };
  }

  getDefaultInitialConditions() {
    return {
      Y: 306.2,
      K: 800,
      L: 600,
      H: 1.0,
      A: 1.0,
      NX: 3.6
    };
  }
}

module.exports = EconomicModelService; 