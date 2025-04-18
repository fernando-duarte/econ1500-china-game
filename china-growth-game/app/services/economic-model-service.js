/**
 * Service for communicating with the economic model microservice
 * Simplified implementation for development
 */
const axios = require('axios');
class EconomicModelService {
  constructor() {
    console.log('Initializing EconomicModelService in mock mode');
    // Set the base URL for API calls
    this.baseUrl = process.env.ECONOMIC_MODEL_URL || 'http://localhost:8000';

    // Mock data for development
    this.mockGameState = {
      teams: [],
      current_round: 0,
      current_year: 1980,
      game_started: false,
      game_ended: false
    };
  }

  async healthCheck() {
    return { status: 'ok', message: 'Mock service running' };
  }

  async getGameState() {
    return this.mockGameState;
  }

  async createTeam(teamName) {
    const newTeam = {
      id: `team-${Date.now()}`,
      name: teamName || `Team ${Math.floor(Math.random() * 1000)}`,
      created_at: new Date().toISOString(),
      current_state: {
        GDP: 306.2,
        Capital: 800,
        'Labor Force': 600,
        'Human Capital': 1.0,
        'Productivity (TFP)': 1.0,
        'Net Exports': 3.6,
        Consumption: 244.96
      },
      history: []
    };

    this.mockGameState.teams.push(newTeam);
    return newTeam;
  }

  async submitDecision(teamId, savingsRate, exchangeRatePolicy) {
    const decision = {
      team_id: teamId,
      round: this.mockGameState.current_round,
      savings_rate: savingsRate,
      exchange_rate_policy: exchangeRatePolicy,
      submitted_at: new Date().toISOString()
    };

    return decision;
  }

  async startGame() {
    this.mockGameState.game_started = true;
    this.mockGameState.current_round = 1;
    this.mockGameState.current_year = 1985;

    return this.mockGameState;
  }

  async advanceRound() {
    this.mockGameState.current_round += 1;
    this.mockGameState.current_year += 5;

    // Simulate updating all teams
    this.mockGameState.teams.forEach(team => {
      // Simulate 3% growth
      team.current_state.GDP *= 1.03;
      team.current_state.Capital *= 1.02;
      team.current_state['Labor Force'] *= 1.01;
      team.current_state['Human Capital'] *= 1.01;
      team.current_state['Productivity (TFP)'] *= 1.01;

      // Add to history
      team.history.push({...team.current_state, round: this.mockGameState.current_round - 1});
    });

    return this.mockGameState;
  }

  // Legacy method for backward compatibility
  async runSimulation(simulationData) {
    try {
      const response = await axios.post(`${this.baseUrl}/simulate`, simulationData);
      return response.data;
    } catch (error) {
      console.error('Economic model simulation failed:', error.message);
      throw error;
    }
  }

  // Game flow methods
  async initializeGame() {
    try {
      const response = await axios.post(`${this.baseUrl}/game/init`);
      return response.data;
    } catch (error) {
      console.error('Failed to initialize game:', error.message);
      throw error;
    }
  }

  // Team management methods
  async getTeamState(teamId) {
    try {
      const response = await axios.get(`${this.baseUrl}/teams/${teamId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get team state for ${teamId}:`, error.message);
      throw error;
    }
  }

  // Results and visualization methods
  async getRankings() {
    try {
      const response = await axios.get(`${this.baseUrl}/results/rankings`);
      return response.data;
    } catch (error) {
      console.error('Failed to get rankings:', error.message);
      throw error;
    }
  }

  async getTeamVisualizations(teamId) {
    try {
      const response = await axios.get(`${this.baseUrl}/results/visualizations/${teamId}`);
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