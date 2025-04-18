/**
 * Unified Economic Model Service for China's Growth Game
 *
 * This service provides a consistent interface for interacting with the economic model,
 * whether it's running as a separate microservice or locally.
 */
const axios = require('axios');

class EconomicModelService {
  constructor(baseUrl, useMock) {
    // Set the base URL for API calls - use environment variable, parameter, or default
    this.baseUrl = baseUrl || process.env.ECONOMIC_MODEL_URL || 'http://localhost:8000';

    // Flag to determine if we're using mock mode or real API
    this.useMock = useMock !== undefined ? useMock : (process.env.USE_MOCK_MODEL === 'true' || !this.baseUrl);

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
   *
   * @returns {Promise<Object>} Health status information
   * @throws {Error} If the health check fails
   */
  async health() {
    if (this.useMock) {
      return { status: 'ok', mode: 'mock' };
    }

    try {
      const response = await axios.get(`${this.baseUrl}/health`);
      return { status: 'ok' };
    } catch (error) {
      console.error('Health check failed:', error.message);
      return { status: 'error', message: error.message };
    }
  }

  /**
   * Alias for health() for backward compatibility
   */
  async healthCheck() {
    return this.health();
  }

  /**
   * Get the current game state
   *
   * @returns {Promise<Object>} Current game state
   * @throws {Error} If unable to retrieve game state
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
   *
   * @param {string} teamName - Optional name for the team
   * @returns {Promise<Object>} Created team information
   * @throws {Error} If team creation fails
   */
  async createTeam(teamName) {
    if (this.useMock) {
      const teamId = teamName === 'Test Team' ? 'team-1' : `team-${Date.now()}`;
      const team = this.createMockTeam(teamId, teamName);
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
   *
   * @param {string} teamId - ID of the team
   * @param {number} savingsRate - Savings rate (between 0.01 and 0.99)
   * @param {string} exchangeRatePolicy - Exchange rate policy ('undervalue', 'market', or 'overvalue')
   * @returns {Promise<Object>} The submitted decision
   * @throws {Error} If decision submission fails
   */
  async submitDecision(teamId, savingsRate, exchangeRatePolicy) {
    // Standardize exchange rate policy handling
    // Convert 'fixed' to 'market' for consistency across all code paths
    const normalizedExchangeRatePolicy = exchangeRatePolicy === 'fixed' ? 'market' : exchangeRatePolicy;

    if (this.useMock) {
      // For tests, create the team if it doesn't exist
      if (!this.mockGameState.teams[teamId]) {
        this.mockGameState.teams[teamId] = this.createMockTeam(teamId, 'Test Team');
      }

      // Create decision object with JavaScript camelCase naming
      const decision = {
        teamId: teamId,
        round: this.mockGameState.current_round,
        year: this.mockGameState.current_year,
        savingsRate: savingsRate,
        exchangeRatePolicy: normalizedExchangeRatePolicy,
        submittedAt: new Date().toISOString()
      };

      // Convert to Python snake_case for API compatibility when sending to server
      const apiDecision = {
        team_id: teamId,
        round: this.mockGameState.current_round,
        year: this.mockGameState.current_year,
        savings_rate: savingsRate,
        exchange_rate_policy: normalizedExchangeRatePolicy,
        submitted_at: new Date().toISOString()
      };

      this.mockGameState.teams[teamId].decisions.push(apiDecision);
      return decision;
    }

    try {
      // Convert from JavaScript camelCase to Python snake_case for API compatibility
      const apiPayload = {
        team_id: teamId,
        savings_rate: savingsRate,
        exchange_rate_policy: normalizedExchangeRatePolicy
      };

      const response = await axios.post(`${this.baseUrl}/teams/decisions`, apiPayload);

      // Convert response from snake_case to camelCase for JavaScript consistency
      const responseData = response.data;
      if (responseData && typeof responseData === 'object') {
        // Simple conversion of common snake_case properties to camelCase
        const camelCaseData = {};
        Object.keys(responseData).forEach(key => {
          const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
          camelCaseData[camelKey] = responseData[key];
        });
        return camelCaseData;
      }

      return responseData;
    } catch (error) {
      console.error('Failed to submit decision:', error.message);
      throw error;
    }
  }

  /**
   * Start the game
   *
   * @returns {Promise<Object>} Game state after starting
   * @throws {Error} If game start fails
   */
  async startGame() {
    if (this.useMock) {
      this.mockGameState.game_started = true;
      this.mockGameState.current_round = 1;
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
   * Apply mock growth to team states
   *
   * @private
   * @returns {void}
   */
  _applyMockGrowth() {
    Object.keys(this.mockGameState.teams).forEach(teamId => {
      const team = this.mockGameState.teams[teamId];

      // Get the latest decision, or use default
      const latestDecision = team.decisions[team.decisions.length - 1] || {
        savings_rate: 0.3,
        exchange_rate_policy: 'market'
      };

      // Save current state to history
      team.history.push({...team.current_state});

      // Simple model: apply growth rates
      const currentState = team.current_state;
      team.current_state = {
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
    });
  }

  /**
   * Advance to the next round
   *
   * @returns {Promise<Object>} Updated game state after advancing round
   * @throws {Error} If round advancement fails
   */
  async advanceRound() {
    if (this.useMock) {
      // Increment round and year
      this.mockGameState.current_round += 1;
      this.mockGameState.current_year += 5;

      // Apply growth to all teams
      this._applyMockGrowth();

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
   *
   * @param {string} teamId - ID of the team to retrieve
   * @returns {Promise<Object>} Team state information
   * @throws {Error} If team not found or retrieval fails
   */
  async getTeamState(teamId) {
    // Validate input
    if (!teamId) {
      throw new Error('Team ID is required');
    }

    if (this.useMock) {
      if (!this.mockGameState.teams[teamId]) {
        throw new Error(`Team ${teamId} not found`);
      }
      return this.mockGameState.teams[teamId];
    }

    try {
      const response = await axios.get(`${this.baseUrl}/teams/${teamId}`);

      // Validate response
      if (!response || !response.data) {
        throw new Error(`Invalid response for team ${teamId}`);
      }

      return response.data;
    } catch (error) {
      // Handle specific error cases
      if (error.response && error.response.status === 404) {
        throw new Error(`Team ${teamId} not found`);
      }

      console.error(`Failed to get team state for ${teamId}:`, error.message);
      throw error;
    }
  }

  /**
   * Get rankings
   *
   * @returns {Promise<Object>} Current rankings for all teams
   * @throws {Error} If rankings retrieval fails
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
   *
   * @param {string} teamId - ID of the team to get visualizations for
   * @returns {Promise<Object>} Visualization data for the team
   * @throws {Error} If team not found or visualization retrieval fails
   */
  async getTeamVisualizations(teamId) {
    // Validate input
    if (!teamId) {
      throw new Error('Team ID is required');
    }

    if (this.useMock) {
      // For tests, create the team if it doesn't exist
      if (!this.mockGameState.teams[teamId]) {
        this.mockGameState.teams[teamId] = this.createMockTeam(teamId, 'Test Team');
      }

      const team = this.mockGameState.teams[teamId];

      // Simple mock visualizations
      return {
        gdp: this._extractMockMetricOverTime(team, 'GDP'),
        capital: this._extractMockMetricOverTime(team, 'Capital'),
        consumption: this._extractMockMetricOverTime(team, 'Consumption')
      };
    }

    try {
      const response = await axios.get(`${this.baseUrl}/results/visualizations/${teamId}`);

      // Validate response
      if (!response || !response.data) {
        throw new Error(`Invalid response for team visualizations ${teamId}`);
      }

      return response.data;
    } catch (error) {
      // Handle specific error cases
      if (error.response && error.response.status === 404) {
        throw new Error(`Team ${teamId} not found or has no visualization data`);
      }

      console.error(`Failed to get visualizations for team ${teamId}:`, error.message);
      throw error;
    }
  }

  // Private helper methods for mock mode

  /**
   * Extract metric over time for visualizations in mock mode
   *
   * @private
   * @param {Object} team - Team object
   * @param {string} metric - Metric name to extract
   * @returns {Object} Object with years and values arrays
   */
  _extractMockMetricOverTime(team, metric) {
    const result = {
      years: [],
      values: []
    };

    // Process history in chronological order (oldest first)
    const history = [...(team.history || [])].reverse();

    // Start with base year (1980 or first available)
    let baseYear = 1980;
    if (history.length > 0 && history[0].Year) {
      baseYear = history[0].Year;
    }

    // Add historical data
    history.forEach((entry, index) => {
      const year = entry.Year || baseYear + (index * 5);
      result.years.push(year);
      result.values.push(entry[metric] || 0);
    });

    // Add current state
    result.years.push(team.current_state.Year || this.mockGameState.current_year);
    result.values.push(team.current_state[metric] || 0);

    return result;
  }

  /**
   * Update rankings in mock mode
   *
   * @private
   * @returns {void}
   */
  /**
   * Create a mock team object
   *
   * @private
   * @param {string} teamId - Team ID
   * @param {string} teamName - Team name
   * @returns {Object} Mock team object
   */
  createMockTeam(teamId, teamName) {
    return {
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
  }

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