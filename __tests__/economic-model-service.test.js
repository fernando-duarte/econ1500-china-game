const EconomicModelService = require('../services/economic-model-service');
const axios = require('axios');

// Mock axios
jest.mock('axios');

describe('EconomicModelService', () => {
  let service;

  beforeEach(() => {
    // Create a new service instance with mock mode enabled
    service = new EconomicModelService('http://localhost:8000', true);

    // Reset axios mocks
    axios.get.mockReset();
    axios.post.mockReset();
  });

  describe('health', () => {
    it('should return health status in mock mode', async () => {
      const result = await service.health();
      expect(result).toEqual({ status: 'ok', mode: 'mock' });
    });

    it('should call the API in real mode', async () => {
      // Create a service in real mode
      const realService = new EconomicModelService('http://localhost:8000', false);

      // Mock the API response
      axios.get.mockResolvedValue({ data: { status: 'ok' } });

      const result = await realService.health();

      expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/health');
      expect(result).toEqual({ status: 'ok' });
    });
  });

  describe('getGameState', () => {
    it('should return mock game state in mock mode', async () => {
      const result = await service.getGameState();

      expect(result).toBeDefined();
      expect(result.current_round).toBeDefined();
      expect(result.teams).toBeDefined();
    });

    it('should call the API in real mode', async () => {
      // Create a service in real mode
      const realService = new EconomicModelService('http://localhost:8000', false);

      // Mock the API response
      axios.get.mockResolvedValue({
        data: {
          current_round: 1,
          teams: {}
        }
      });

      const result = await realService.getGameState();

      expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/game/state');
      expect(result).toEqual({ current_round: 1, teams: {} });
    });
  });

  describe('submitDecision', () => {
    it('should submit decision in mock mode', async () => {
      // First create a team
      await service.createTeam('Test Team');

      // Then submit a decision
      const result = await service.submitDecision('team-1', 0.5, 'market');

      expect(result).toBeDefined();
      expect(result.teamId).toBe('team-1');
      expect(result.savingsRate).toBe(0.5);
      expect(result.exchangeRatePolicy).toBe('market');
    });

    it('should call the API in real mode', async () => {
      // Create a service in real mode
      const realService = new EconomicModelService('http://localhost:8000', false);

      // Mock the API response
      axios.post.mockResolvedValue({
        data: {
          team_id: 'team-1',
          savings_rate: 0.5,
          exchange_rate_policy: 'market'
        }
      });

      const result = await realService.submitDecision('team-1', 0.5, 'market');

      expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/teams/decisions', {
        team_id: 'team-1',
        savings_rate: 0.5,
        exchange_rate_policy: 'market'
      });

      expect(result).toEqual({
        teamId: 'team-1',
        savingsRate: 0.5,
        exchangeRatePolicy: 'market'
      });
    });
  });

  describe('startGame', () => {
    it('should start game in mock mode', async () => {
      const result = await service.startGame();

      expect(result).toBeDefined();
      expect(result.current_round).toBe(1);
    });
  });

  describe('advanceRound', () => {
    it('should advance round in mock mode', async () => {
      // Start the game
      await service.startGame();

      // Get initial round
      const initialState = await service.getGameState();
      const initialRound = initialState.current_round;

      // Advance round
      const result = await service.advanceRound();

      expect(result).toBeDefined();
      expect(result.current_round).toBe(initialRound + 1);
    });
  });

  describe('getTeamVisualizations', () => {
    it('should get visualizations in mock mode', async () => {
      // First create a team
      await service.createTeam('Test Team');

      // Then get visualizations
      const result = await service.getTeamVisualizations('team-1');

      expect(result).toBeDefined();
      expect(result.gdp).toBeDefined();
      expect(result.gdp.years).toBeInstanceOf(Array);
      expect(result.gdp.values).toBeInstanceOf(Array);
    });
  });
});
