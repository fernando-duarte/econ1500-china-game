/**
 * Unified Economic Model Service for China's Growth Game
 * 
 * This service provides a consistent interface for interacting with the economic model,
 * whether it's running as a separate microservice or locally.
 */
const axios = require('axios');

class EconomicModelService {
  constructor() {
    // Set the base URL for API calls - use environment variable or default
    this.baseUrl = process.env.ECONOMIC_MODEL_URL || 'http://localhost:8000';
    
    // Flag to determine if we're using mock mode or real API
    this.useMock = process.env.USE_MOCK_MODEL === 'true' || !this.baseUrl;
    
    console.log(`Initializing EconomicModelService in ${this.useMock ? 'mock' : 'API'} mode`);
    
    // Initial game state for mock mode
    this.mockGameState = {
      game_id: `mock-${Date.now()}`,
      teams: {},
      current_round: 0,
      current_year: 1980,
      game_started: false,
      game_ended: false,
      rankings: {
        gdp: [],
        growth: [],
        consumption: []
      }
    };
  }

  /**
   * Check the health of the economic model service
   */
  async healthCheck() {
    if (this.useMock) {
      return { status: 'ok', message: 'Mock service running', mode: 'mock' };
    }
    
    try {
      const response = await axios.get(`${this.baseUrl}/health`);
      return { ...response.data, mode: 'api' };
    } catch (error) {
      console.error('Health check failed:', error.message);
      return { status: 'error', message: error.message, mode: 'api_error' };
    }
  }

  /**
   * Get the current game state
   */
  async getGameState() {
    if (this.useMock) {
      return this.mockGameState;
    }
    
    try {
      const response = await axios.get(`${this.baseUrl}/game/state`);
      return response.data;
    } catch (error) {
      console.error('Failed to get game state:', error.message);
      throw error;
    }
  }

  /**
   * Create a new team
   */
  async createTeam(teamName) {
    if (this.useMock) {
      const teamId = `team-${Date.now()}`;
      const team = {
        id: teamId,
        team_id: teamId,
        name: teamName || `Team ${Object.keys(this.mockGameState.teams).length + 1}`,
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
        history: [],
        decisions: [
          {
            round: 0,
            year: 1980,
            savings_rate: 0.3,
            exchange_rate_policy: 'market'
          }
        ],
        eliminated: false
      };

      this.mockGameState.teams[teamId] = team;
      return team;
    }
    
    try {
      const response = await axios.post(`${this.baseUrl}/teams/create`, { team_name: teamName });
      return response.data;
    } catch (error) {
      console.error('Failed to create team:', error.message);
      throw error;
    }
  }

  /**
   * Submit a decision for a team
   */
  async submitDecision(teamId, savingsRate, exchangeRatePolicy) {
    if (this.useMock) {
      if (!this.mockGameState.teams[teamId]) {
        throw new Error(`Team ${teamId} not found`);
      }

      const decision = {
        team_id: teamId,
        round: this.mockGameState.current_round,
        year: this.mockGameState.current_year,
        savings_rate: savingsRate,
        exchange_rate_policy: exchangeRatePolicy,
        submitted_at: new Date().toISOString()
      };

      this.mockGameState.teams[teamId].decisions.push(decision);
      return decision;
    }
    
    try {
      const response = await axios.post(`${this.baseUrl}/teams/decisions`, {
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

  /**
   * Start the game
   */
  async startGame() {
    if (this.useMock) {
      this.mockGameState.game_started = true;
      this.mockGameState.current_round = 0;
      this.mockGameState.current_year = 1980;
      
      // Initialize history for all teams
      Object.keys(this.mockGameState.teams).forEach(teamId => {
        const team = this.mockGameState.teams[teamId];
        team.history = [{ ...team.current_state }];
      });
      
      return this.mockGameState;
    }
    
    try {
      // First initialize the game if needed
      try {
        await axios.post(`${this.baseUrl}/game/init`);
      } catch (error) {
        // If it fails because game is already initialized, that's ok
        console.log('Game initialization step:', error.message);
      }
      
      // Then start the game
      const response = await axios.post(`${this.baseUrl}/game/start`);
      return response.data;
    } catch (error) {
      console.error('Failed to start game:', error.message);
      throw error;
    }
  }

  /**
   * Advance to the next round
   */
  async advanceRound() {
    if (this.useMock) {
      // Increment round and year
      this.mockGameState.current_round += 1;
      this.mockGameState.current_year += 5;
      
      // Update team states
      Object.keys(this.mockGameState.teams).forEach(teamId => {
        const team = this.mockGameState.teams[teamId];
        
        // Get the latest decision, or use default
        const latestDecision = team.decisions[team.decisions.length - 1] || {
          savings_rate: 0.3,
          exchange_rate_policy: 'market'
        };
        
        // Simple model: apply growth rates
        const currentState = team.current_state;
        const newState = {
          Year: this.mockGameState.current_year,
          Round: this.mockGameState.current_round,
          GDP: currentState.GDP * 1.03,
          Capital: currentState.Capital * 1.02,
          'Labor Force': currentState['Labor Force'] * 1.01,
          'Human Capital': currentState['Human Capital'] * 1.01,
          'Productivity (TFP)': currentState['Productivity (TFP)'] * 1.01,
          'Net Exports': currentState['Net Exports'] * 1.02,
          Consumption: currentState.GDP * 0.7, // ~70% consumption
          Investment: currentState.GDP * 0.3  // ~30% investment
        };
        
        // Save current state to history
        team.history.push({...currentState});
        
        // Update current state
        team.current_state = newState;
      });
      
      // Update rankings
      this.updateMockRankings();
      
      return this.mockGameState;
    }
    
    try {
      const response = await axios.post(`${this.baseUrl}/game/next-round`);
      return response.data;
    } catch (error) {
      console.error('Failed to advance round:', error.message);
      throw error;
    }
  }

  /**
   * Get team state
   */
  async getTeamState(teamId) {
    if (this.useMock) {
      if (!this.mockGameState.teams[teamId]) {
        throw new Error(`Team ${teamId} not found`);
      }
      return this.mockGameState.teams[teamId];
    }
    
    try {
      const response = await axios.get(`${this.baseUrl}/teams/${teamId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get team state for ${teamId}:`, error.message);
      throw error;
    }
  }

  /**
   * Get rankings
   */
  async getRankings() {
    if (this.useMock) {
      return this.mockGameState.rankings;
    }
    
    try {
      const response = await axios.get(`${this.baseUrl}/results/rankings`);
      return response.data;
    } catch (error) {
      console.error('Failed to get rankings:', error.message);
      throw error;
    }
  }

  /**
   * Get visualizations for a team
   */
  async getTeamVisualizations(teamId) {
    if (this.useMock) {
      if (!this.mockGameState.teams[teamId]) {
        throw new Error(`Team ${teamId} not found`);
      }
      
      const team = this.mockGameState.teams[teamId];
      
      // Simple mock visualizations
      return {
        gdp_over_time: this._extractMockMetricOverTime(team, 'GDP'),
        capital_over_time: this._extractMockMetricOverTime(team, 'Capital'),
        consumption_over_time: this._extractMockMetricOverTime(team, 'Consumption')
      };
    }
    
    try {
      const response = await axios.get(`${this.baseUrl}/results/visualizations/${teamId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get visualizations for team ${teamId}:`, error.message);
      throw error;
    }
  }

  // Private helper methods for mock mode
  
  /**
   * Extract metric over time for visualizations in mock mode
   */
  _extractMockMetricOverTime(team, metric) {
    const years = [];
    const values = [];
    
    // Add current state
    years.push(team.current_state.Year || this.mockGameState.current_year);
    values.push(team.current_state[metric] || 0);
    
    // Add historical data
    for (const entry of team.history || []) {
      if (entry.Year) years.push(entry.Year);
      else years.push(years.length > 0 ? years[0] - 5 : 1980);
      
      values.push(entry[metric] || 0);
    }
    
    return {
      years,
      values
    };
  }
  
  /**
   * Update rankings in mock mode
   */
  updateMockRankings() {
    const teams = this.mockGameState.teams;
    const teamIds = Object.keys(teams);
    
    // GDP ranking
    const gdpRanking = [...teamIds].sort((a, b) => {
      return teams[b].current_state.GDP - teams[a].current_state.GDP;
    });
    
    // Growth ranking (simplified: just based on current GDP)
    const growthRanking = [...gdpRanking];
    
    // Consumption ranking
    const consumptionRanking = [...teamIds].sort((a, b) => {
      return teams[b].current_state.Consumption - teams[a].current_state.Consumption;
    });
    
    this.mockGameState.rankings = {
      gdp: gdpRanking,
      growth: growthRanking,
      consumption: consumptionRanking
    };
  }
}

module.exports = EconomicModelService; 